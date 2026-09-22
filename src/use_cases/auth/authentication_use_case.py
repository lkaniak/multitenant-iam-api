import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import pyotp

from config import settings
from entities.enum import OrganizationActionTypeActivityEnum, UserTypeEnum
from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from entities.exceptions import (
    UnauthorizedAppException,
    FailedToSendMfaOtpCodeException,
    MfaOtpCodeInvalidException,
)
from entities.exceptions.insufficient_permissions_exception import InsufficientPermissionsException
from notification_service import Notification, NotificationPort
from services.alert.alert_dispatch_service import AlertDispatchService
from entities.user_entity import UserEntity
from infra.repositories.user_repository import UserRepository
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.request.organization_user_groups.organization_user_groups_filter_request import (
    OrganizationUserGroupsFilter,
)
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.token_response import TokenBase
from use_cases.auth.authorization_use_case import AuthorizationUseCase
from use_cases.organization import OrganizationUseCase
from use_cases.organization_user_groups import OrganizationUserGroupsUseCase
from use_cases.user import UserUseCase


class AuthenticationUseCase:
    def __init__(self):
        pass

    @classmethod
    def authenticate(cls, user: UserEntity) -> TokenBase:
        return cls.create_token(user)

    @classmethod
    def create_token(
        cls, user: UserEntity, change_organization_id: Optional[str] = None
    ) -> TokenBase:
        activity = (
            OrganizationActionTypeActivityEnum.CHANGE_ORGANIZATION
            if change_organization_id
            else OrganizationActionTypeActivityEnum.SIGNIN
        )
        organization_use_case = OrganizationUseCase()
        token_duration = timedelta(days=1)
        now = datetime.now(timezone.utc)
        issued_at = now
        expiration = now + token_duration
        not_before = now

        organization_id = change_organization_id or user.organization_id
        if not organization_id and user.user_type == UserTypeEnum.SYSTEM_ADMIN.value:
            organization_id = organization_use_case.get_first_organization().id

        data = {
            "sub": user.id,
            "organization_id": organization_id,
            "iat": issued_at,
            "exp": expiration,
            "nbf": not_before,
            "jti": secrets.token_urlsafe(32),
            "type": "access",
            "aud": AuthorizationUseCase.return_audience_per_user_type(
                UserTypeEnum.from_str(user.user_type)
            ),
        }

        organization = organization_use_case.get_organization(
            filter=OrganizationFilter(id=organization_id)
        )
        UserUseCase().register_user_activity(user, organization, activity)

        return TokenBase(
            access_token=jwt.encode(
                data, settings.AUTH_SECRET_KEY, algorithm=settings.AUTH_ALGORITHM
            ),
            expiration=int(token_duration.total_seconds()),
        )

    @classmethod
    def decode_jwt_payload(cls, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.AUTH_SECRET_KEY,
                algorithms=settings.AUTH_ALGORITHM,
                audience=settings.API_URL,
            )
        except jwt.InvalidAudienceError:
            raise UnauthorizedAppException()
        except jwt.PyJWTError:
            raise UnauthorizedAppException()

    @classmethod
    def get_user_by_token(cls, token: str, notifications: NotificationPort) -> Optional[UserEntity]:
        payload = cls.decode_jwt_payload(token)
        user_id = payload["sub"]
        if user := UserRepository().get_user(UserFilter(id=user_id)):
            if user.settings.inactive:
                return None
            user_groups = OrganizationUserGroupsUseCase().get_my_user_groups_organizations(
                filter=OrganizationUserGroupsFilter(user_id=user.id)
            )
            payload_organization_id = payload["organization_id"]
            organizations_allowed_for_user = [
                organization.id for organization in user_groups.organizations
            ]
            authorized = (
                user.user_type == UserTypeEnum.SYSTEM_ADMIN.value
                or payload_organization_id in organizations_allowed_for_user
                or payload_organization_id == user.organization_id
            )
            if not authorized:
                cls.notify_permission_denied(
                    organization_id=payload_organization_id,
                    notifications=notifications,
                    data={"user_id": user.id, "username": user.username},
                )
                raise InsufficientPermissionsException()
            user.organization_id = payload_organization_id
            return user
        return None

    @classmethod
    def notify_login_failed(cls, user: UserEntity, notifications: NotificationPort) -> None:
        AlertDispatchService(notifications).dispatch(
            event_type=AlertEventTypeEnum.LOGIN_FAILED,
            organization_id=user.organization_id,
            data={"user_id": user.id, "username": user.username},
        )

    @classmethod
    def notify_permission_denied(
        cls,
        organization_id: str | None,
        notifications: NotificationPort,
        data: dict | None = None,
    ) -> None:
        AuthorizationUseCase.notify_permission_denied(
            organization_id=organization_id, notifications=notifications, data=data
        )

    @classmethod
    def login_with_mfa(cls, user: UserEntity, notifications: NotificationPort):
        temporary_otp_code = AuthenticationUseCase.generate_mfa_otp_code(user.username)
        try:
            notifications.send(
                Notification(
                    channel="email",
                    destination=user.contact_info.email,
                    payload={
                        "kind": "mfa_otp",
                        "username": user.username,
                        "temporary_otp_code": temporary_otp_code,
                    },
                )
            )
        except Exception:
            raise FailedToSendMfaOtpCodeException()

    @classmethod
    def _derive_mfa_secret(cls, username: str) -> str:
        key_material = hashlib.pbkdf2_hmac(
            "sha256",
            settings.MFA_SECRET_KEY.encode("utf-8"),
            username.encode("utf-8"),
            iterations=120000,
            dklen=20,
        )
        return base64.b32encode(key_material).decode("utf-8").rstrip("=")

    @classmethod
    def validate_mfa_otp_code(cls, username: str, received_otp: str):
        secret_key = cls._derive_mfa_secret(username)
        totp = pyotp.TOTP(secret_key, interval=settings.EXPIRATION_MFA_OTP_CODE_IN_SECONDS)

        if not totp.verify(received_otp):
            raise MfaOtpCodeInvalidException()

    @classmethod
    def generate_mfa_otp_code(cls, username: str) -> str:
        secret_key = cls._derive_mfa_secret(username)
        totp = pyotp.TOTP(secret_key, interval=settings.EXPIRATION_MFA_OTP_CODE_IN_SECONDS)
        return totp.now()
