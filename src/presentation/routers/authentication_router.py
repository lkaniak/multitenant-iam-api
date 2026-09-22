from fastapi import APIRouter, Depends, Form, status

from common.security.permission_handler import get_all_permissions
from entities.enum.user_type_enum import UserTypeEnum
from entities.user_entity import UserEntity
from notification_service import NotificationPort

from presentation.dependencies.notification_service import get_notifications
from presentation.middleware.auth import (
    RoleAndTypeChecker,
    verify_challenge,
    verify_organization,
)
from presentation.response.token_response import TokenBase
from use_cases.auth.authentication_use_case import AuthenticationUseCase
from use_cases.auth.authorization_use_case import AuthorizationUseCase

api_router = APIRouter()
tags = ["Auth"]


@api_router.post("/", status_code=status.HTTP_200_OK, tags=tags, summary="Login with MFA")
def login_with_mfa(
    user: UserEntity = Depends(verify_challenge),
    notifications: NotificationPort = Depends(get_notifications),
):
    AuthenticationUseCase.login_with_mfa(user, notifications)

    return


@api_router.post(
    "/validate_mfa_otp_code",
    response_model=TokenBase,
    status_code=status.HTTP_200_OK,
    tags=tags,
    summary="Validate MFA otp code",
)
def validate_otp(
    temporary_otp_code: str = Form(...),
    user: UserEntity = Depends(verify_challenge),
):
    AuthenticationUseCase.validate_mfa_otp_code(
        username=user.username, received_otp=temporary_otp_code
    )

    return AuthenticationUseCase.authenticate(user)


@api_router.get(
    "/organization/{organization_id}",
    response_model=TokenBase,
    tags=tags,
    summary="Change organization",
)
def change_organization(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_all_permissions())
    ),
    organization_id: str = Depends(verify_organization),
    notifications: NotificationPort = Depends(get_notifications),
):
    AuthorizationUseCase.check_user_has_access_to_organization(
        user_type=UserTypeEnum.from_str(logged_user.user_type),
        user_id=logged_user.id,
        organization_id_requested=organization_id,
        notifications=notifications,
    )
    return AuthenticationUseCase.create_token(logged_user, change_organization_id=organization_id)


auth_router = {"router": api_router, "prefix": "/auth", "tags": tags}
