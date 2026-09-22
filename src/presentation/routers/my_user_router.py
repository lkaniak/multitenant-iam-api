from fastapi import APIRouter, Body, Depends, status

from common.security.permission_handler import (
    get_all_permissions,
)
from entities import UserEntity
from notification_service import NotificationPort

from presentation.dependencies.notification_service import get_notifications
from presentation.middleware.auth import RoleAndTypeChecker
from presentation.request.user.patch_requests import (
    PatchMyUserRequest,
    PatchUserRequest,
    PatchUserSettingsRequest,
    ResetPasswordRequest,
)
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.user.get_user_response import GetMyUserResponse
from presentation.request.organization_user_groups.organization_user_groups_filter_request import (
    OrganizationUserGroupsFilter,
)
from presentation.response.organization_user_groups.get_organization_user_groups_response import (
    GetMyUserGroupsOrganizationsResponse,
)
from use_cases.organization_user_groups import OrganizationUserGroupsUseCase
from use_cases import UserUseCase

api_router = APIRouter()
tags = ["User"]


@api_router.get(
    "/my/user",
    status_code=status.HTTP_200_OK,
    description="Get logged user",
    tags=tags + ["my"],
    response_model=GetMyUserResponse,
    response_model_exclude_unset=True,
)
def get_my_user(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_all_permissions())
    ),
) -> GetMyUserResponse:
    filter = UserFilter(id=logged_user.id)
    user = UserUseCase().get_my_user(filter=filter, organization_id=logged_user.organization_id)
    return user


@api_router.patch(
    "/my/user",
    status_code=status.HTTP_200_OK,
    description="Patch logged user",
    tags=tags + ["my"],
    response_model=GetMyUserResponse,
    response_model_exclude_unset=True,
)
def patch_my_user(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_all_permissions())
    ),
    user_payload: PatchMyUserRequest = Body(...),
    notifications: NotificationPort = Depends(get_notifications),
) -> GetMyUserResponse:
    filter = UserFilter(id=logged_user.id)
    patch_user_payload = PatchUserRequest(
        id=logged_user.id,
        password=user_payload.new_password,
        **user_payload.model_dump(),
    )
    UserUseCase().patch_user(user=patch_user_payload, notifications=notifications)
    user = UserUseCase().get_my_user(filter=filter, organization_id=logged_user.organization_id)
    return user


@api_router.patch(
    "/my/user/settings",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Patch logged user settings",
    tags=tags + ["my"],
    response_model=None,
    response_model_exclude_unset=True,
)
def patch_my_user_settings(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_all_permissions())
    ),
    settings_payload: PatchUserSettingsRequest = Body(...),
) -> None:
    UserUseCase().patch_user_settings(user_id=logged_user.id, configuration=settings_payload)
    return None


@api_router.put(
    "/reset/my/password",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Send reset password email",
    tags=tags + ["my"],
    response_model=None,
    response_model_exclude_unset=True,
)
def reset_my_password(
    user_payload: ResetPasswordRequest = Body(...),
    notifications: NotificationPort = Depends(get_notifications),
) -> None:
    UserUseCase().send_reset_password_request(payload=user_payload, notifications=notifications)


@api_router.get(
    "/my/user/groups/organizations",
    status_code=status.HTTP_200_OK,
    description="Get logged user organizations by group",
    tags=tags + ["Organization User Groups"] + ["my"],
    response_model=GetMyUserGroupsOrganizationsResponse,
    response_model_exclude_unset=True,
)
def get_my_user_groups_organizations(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_all_permissions())
    ),
) -> GetMyUserGroupsOrganizationsResponse:
    filter = OrganizationUserGroupsFilter(user_id=logged_user.id)
    return OrganizationUserGroupsUseCase().get_my_user_groups_organizations(filter=filter)


my_user_router = {"router": api_router, "tags": tags}
