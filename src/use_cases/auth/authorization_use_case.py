import re

from config import settings
from entities import (
    AuthorizationRequestedEntity,
    AuthorizationRequestorEntity,
    OrganizationEntity,
    UserEntity,
)
from entities.enum import (
    RoleEnum,
    UserTypeEnum,
    ValidationErrorCodeEnum,
    JobPositionEnum,
    ActivityAreaEnum,
    AffiliationTypeEnum,
)
from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from entities.exceptions.insufficient_permissions_exception import InsufficientPermissionsException
from infra.repositories import OrganizationRepository, UserRepository
from notification_service import NotificationPort
from services.alert.alert_dispatch_service import AlertDispatchService
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.request.user.user_filter_request import UserFilter
from use_cases.organization_user_groups import OrganizationUserGroupsUseCase
from presentation.request.organization_user_groups.organization_user_groups_filter_request import (
    OrganizationUserGroupsFilter,
)


class AuthorizationUseCase:

    @classmethod
    def check_contact_info_is_valid(
        cls, user_type: str, contact_info: dict
    ) -> list[ValidationErrorCodeEnum]:
        errors = []
        if user_type == UserTypeEnum.SYSTEM_ADMIN.value:
            return errors
        valid_job_positions = [member.value for member in JobPositionEnum]
        valid_activity_areas = [member.value for member in ActivityAreaEnum]
        valid_affiliation_types = [member.value for member in AffiliationTypeEnum]
        if contact_info.get("job_position", None) not in valid_job_positions:
            errors.append(("job_position", valid_job_positions))
        if contact_info.get("activity_area", None) not in valid_activity_areas:
            errors.append(("activity_area", valid_activity_areas))
        if contact_info.get("affiliation_type", None) not in valid_affiliation_types:
            errors.append(("affiliation_type", valid_affiliation_types))
        return errors

    @classmethod
    def role_is_allowed(cls, requestor_role: RoleEnum, role_needed: RoleEnum):
        if requestor_role in [RoleEnum.OWNER, RoleEnum.ADMIN]:
            return True

        return requestor_role == role_needed and requestor_role == RoleEnum.REGULAR

    @classmethod
    def user_type_is_allowed(
        cls, requestor_user_type: UserTypeEnum, user_type_needed: UserTypeEnum
    ):
        if (
            requestor_user_type == UserTypeEnum.OTHER
            and user_type_needed == UserTypeEnum.SYSTEM_ADMIN
        ):
            return False
        return True

    @classmethod
    def password_invalid(cls, password: str) -> list[ValidationErrorCodeEnum]:
        errors = []
        if not password:
            return [ValidationErrorCodeEnum.PASSWORD_MISSING_LENGTH]
        if len(password) < settings.MIN_PASSWORD_LENGTH:
            errors.append(ValidationErrorCodeEnum.PASSWORD_MISSING_LENGTH)

        if not re.search(r"\d", password):
            errors.append(ValidationErrorCodeEnum.PASSWORD_MISSING_NUMBERS)

        if not re.search(r"^(?=.*[a-z])(?=.*[A-Z]).+$", password):
            errors.append(ValidationErrorCodeEnum.PASSWORD_MISSING_UPPERCASE_LOWERCASE)

        if not re.search(r"[^a-zA-Z0-9]", password):
            errors.append(ValidationErrorCodeEnum.PASSWORD_MISSING_SPECIAL_CHARS)

        return errors

    @classmethod
    def password_matches_old(cls, password: str, user_id: str) -> bool:
        if user := UserRepository().get_user(UserFilter(id=user_id)):
            from use_cases.user.user_helpers import verify_password

            return verify_password(password, user.password)
        return False

    @classmethod
    def user_exists(cls, user_id: str) -> UserEntity:
        if user := UserRepository().get_user(UserFilter(id=user_id)):
            return user

    @classmethod
    def username_exists(cls, username: str) -> UserEntity:
        if user := UserRepository().get_user(UserFilter(username=username.lower())):
            return user

    @classmethod
    def organization_id_exists(cls, organization_id: str) -> OrganizationEntity:
        if organization := OrganizationRepository().get_organization(
            OrganizationFilter(id=organization_id)
        ):
            return organization

    @classmethod
    def check_password(cls, challenge: str, password: str) -> bool:
        from use_cases.user.user_helpers import verify_password

        return verify_password(challenge, password)

    @classmethod
    def check_organization_inactivity(cls, organization_id: str) -> bool:
        if organization := OrganizationRepository().get_organization(
            OrganizationFilter(id=organization_id)
        ):
            return organization.inactive
        return False

    @classmethod
    def notify_permission_denied(
        cls,
        organization_id: str | None,
        notifications: NotificationPort,
        data: dict | None = None,
    ) -> None:
        AlertDispatchService(notifications).dispatch(
            event_type=AlertEventTypeEnum.PERMISSION_DENIED,
            organization_id=organization_id,
            data=data or {},
        )

    @classmethod
    def _deny(
        cls,
        organization_id: str | None,
        notifications: NotificationPort,
        data: dict | None = None,
        internal: str = None,
    ):
        cls.notify_permission_denied(
            organization_id=organization_id, notifications=notifications, data=data
        )
        raise InsufficientPermissionsException(internal=internal)

    @classmethod
    def check_privileges(
        cls,
        requestor: AuthorizationRequestorEntity,
        requested: AuthorizationRequestedEntity,
        notifications: NotificationPort,
    ) -> None:
        denial = {
            "requestor_organization_id": requestor.organization_id,
            "requested_organization_id": requested.organization_id,
            "requestor_role": requestor.role.value if requestor.role else None,
            "requested_role": requested.role.value if requested.role else None,
        }

        if requestor.user_type == UserTypeEnum.SYSTEM_ADMIN:
            if requestor.role == RoleEnum.ADMIN:
                return

            if (
                requested.role == RoleEnum.ADMIN
                and requested.user_type == UserTypeEnum.SYSTEM_ADMIN
            ):
                cls._deny(
                    organization_id=requestor.organization_id,
                    notifications=notifications,
                    data=denial,
                )

            if requested.role in [RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.REGULAR]:
                return

        if not cls.user_type_is_allowed(
            requestor_user_type=requested.user_type, user_type_needed=requestor.user_type
        ):
            cls._deny(
                organization_id=requestor.organization_id,
                notifications=notifications,
                data=denial,
            )

        if (
            requestor.organization_id != requested.organization_id
            and requestor.user_type != UserTypeEnum.SYSTEM_ADMIN
        ):
            cls._deny(
                organization_id=requestor.organization_id,
                notifications=notifications,
                data=denial,
            )

        if requested.role and not cls.role_is_allowed(
            requestor_role=requestor.role, role_needed=requested.role
        ):
            cls._deny(
                organization_id=requestor.organization_id,
                notifications=notifications,
                data=denial,
            )

        if requested.role and (
            requestor.role != RoleEnum.OWNER and requested.role in (RoleEnum.OWNER, RoleEnum.ADMIN)
        ):
            cls._deny(
                organization_id=requestor.organization_id,
                notifications=notifications,
                data=denial,
            )

    @classmethod
    def return_audience_per_user_type(cls, user_type: UserTypeEnum) -> list[str]:
        audiences = [
            settings.API_URL,
            settings.APP_CLIENT_URL,
        ]
        return audiences

    @classmethod
    def check_user_has_access_to_organization(
        cls,
        user_type: UserTypeEnum,
        user_id: str,
        organization_id_requested: str,
        notifications: NotificationPort,
    ):
        if user_type == UserTypeEnum.SYSTEM_ADMIN:
            return
        get_user_groups = OrganizationUserGroupsUseCase().get_my_user_groups_organizations(
            filter=OrganizationUserGroupsFilter(user_id=user_id)
        )
        organization_ids = [organization.id for organization in get_user_groups.organizations]
        if organization_id_requested not in organization_ids:
            cls._deny(
                organization_id=organization_id_requested,
                notifications=notifications,
                data={
                    "user_id": user_id,
                    "requested_organization_id": organization_id_requested,
                },
                internal=f"User {user_id} tried to access organization {organization_id_requested}",
            )
