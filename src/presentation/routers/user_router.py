from typing import Callable, Optional

from fastapi import APIRouter, Body, Depends, status

from common.security.permission_handler import get_admin_permissions, get_restricted_permissions
from entities import AuthorizationRequestedEntity, UserEntity
from entities.enum import RoleEnum, UserTypeEnum
from entities.exceptions.user_exceptions import NoUserFoundException
from notification_service import NotificationPort

from presentation.dependencies.notification_service import get_notifications
from presentation.middleware.auth import (
    BulkPrivilegesChecker,
    PrivilegesChecker,
    RoleAndTypeChecker,
)
from presentation.middleware.verify_object_id import verify_object_id
from presentation.request.user.create_user_requests import CreateUserRequest, CreateUsersRequest
from presentation.request.user.patch_requests import (
    PatchUserContactInfoRequest,
    PatchUserRequest,
    PatchUserSettingsRequest,
    PatchUserTelemetryRequest,
)
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.user.create_user_response import CreateUserResponse
from presentation.response.user.get_user_response import GetUserResponse, GetUsersResponse
from use_cases import UserUseCase

api_router = APIRouter()
tags = ["User"]


def _build_requested_from_user(user: UserEntity) -> AuthorizationRequestedEntity:
    return AuthorizationRequestedEntity(
        organization_id=user.organization_id,
        user_type=UserTypeEnum.from_str(user.user_type),
        role=RoleEnum.from_str(user.role),
    )


def _build_requested_from_create_payload(
    payload: CreateUserRequest,
) -> AuthorizationRequestedEntity:
    role_str = (
        payload.role
        if payload.user_type != UserTypeEnum.SYSTEM_ADMIN.value
        else RoleEnum.ADMIN.value
    )
    return AuthorizationRequestedEntity(
        role=RoleEnum.from_str(role_str),
        organization_id=payload.organization_id,
        user_type=UserTypeEnum.from_str(payload.user_type),
    )


def _build_requested_from_patch_user_context(
    context: tuple[PatchUserRequest, UserEntity],
) -> AuthorizationRequestedEntity:
    payload, user_to_change = context
    return AuthorizationRequestedEntity(
        role=RoleEnum.from_str(payload.role),
        organization_id=user_to_change.organization_id,
        user_type=UserTypeEnum.from_str(user_to_change.user_type),
    )


@api_router.get(
    "/users/app",
    status_code=status.HTTP_200_OK,
    description="Get all app users",
    tags=tags,
    response_model=list[GetUsersResponse],
    response_model_exclude_unset=True,
)
def get_app_users(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
) -> list[GetUsersResponse]:
    return UserUseCase().get_all_app_users()


@api_router.get(
    "/users/organization/{id}",
    status_code=status.HTTP_200_OK,
    description="Get users by organization_id",
    tags=tags,
    response_model=list[GetUserResponse],
    response_model_exclude_unset=True,
)
def get_users_by_organization_id(
    id: str = Depends(verify_object_id),
    role: Optional[str] = None,
    user_type: Optional[str] = None,
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
) -> list[GetUserResponse]:
    return UserUseCase().get_users(
        filter=UserFilter(role=role, user_type=user_type, organization_id=id)
    )


@api_router.get(
    "/user",
    status_code=status.HTTP_200_OK,
    description="Get user",
    tags=tags,
    response_model=GetUserResponse,
    response_model_exclude_unset=True,
)
def get_user(
    id: Optional[str] = None,
    username: Optional[str] = None,
    check_privileges: Callable[..., None] = Depends(
        PrivilegesChecker(get_admin_permissions(), _build_requested_from_user)
    ),
) -> GetUserResponse:
    filter = UserFilter(id=id, username=username)
    if user := UserUseCase().get_user_internal(filter=filter):
        check_privileges(user)
        return user
    raise NoUserFoundException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
    description="Create user",
    tags=tags,
    response_model=CreateUserResponse,
    response_model_exclude_unset=True,
)
def create_user(
    check_privileges: Callable[..., None] = Depends(
        PrivilegesChecker(get_admin_permissions(), _build_requested_from_create_payload)
    ),
    user_payload: CreateUserRequest = Body(...),
    notifications: NotificationPort = Depends(get_notifications),
) -> CreateUserResponse:
    check_privileges(user_payload)
    return UserUseCase().create_user(user=user_payload, notifications=notifications)


@api_router.post(
    "/users",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Create users",
    tags=tags,
    response_model=None,
)
def create_users(
    check_privileges: Callable[..., None] = Depends(
        BulkPrivilegesChecker(get_admin_permissions(), _build_requested_from_create_payload)
    ),
    user_payload: CreateUsersRequest = Body(...),
    notifications: NotificationPort = Depends(get_notifications),
) -> None:
    check_privileges(user_payload.users)
    UserUseCase().create_users(users=user_payload.users, notifications=notifications)


@api_router.patch(
    "/user",
    status_code=status.HTTP_200_OK,
    description="Patch user",
    tags=tags,
    response_model=GetUserResponse,
    response_model_exclude_unset=True,
)
def patch_user(
    check_privileges: Callable[..., None] = Depends(
        PrivilegesChecker(get_admin_permissions(), _build_requested_from_patch_user_context)
    ),
    user_payload: PatchUserRequest = Body(...),
    notifications: NotificationPort = Depends(get_notifications),
) -> list[GetUserResponse]:
    if user_to_change := UserUseCase().get_user_internal(filter=UserFilter(id=user_payload.id)):
        check_privileges((user_payload, user_to_change))
        return UserUseCase().patch_user(user=user_payload, notifications=notifications)
    raise NoUserFoundException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.patch(
    "/user/{id}/settings",
    status_code=status.HTTP_200_OK,
    description="Patch user settings",
    tags=tags,
    response_model=GetUserResponse,
    response_model_exclude_unset=True,
)
def patch_user_settings(
    id: str = Depends(verify_object_id),
    check_privileges: Callable[..., None] = Depends(
        PrivilegesChecker(get_admin_permissions(), _build_requested_from_user)
    ),
    settings_payload: PatchUserSettingsRequest = Body(...),
) -> list[GetUserResponse]:
    if user_to_change := UserUseCase().get_user_internal(filter=UserFilter(id=id)):
        check_privileges(user_to_change)
        return UserUseCase().patch_user_settings(user_id=id, configuration=settings_payload)
    raise NoUserFoundException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.patch(
    "/user/{id}/telemetry",
    status_code=status.HTTP_200_OK,
    description="Patch user telemetry",
    tags=tags,
    response_model=GetUserResponse,
    response_model_exclude_unset=True,
)
def patch_user_telemetry(
    id: str = Depends(verify_object_id),
    check_privileges: Callable[..., None] = Depends(
        PrivilegesChecker(get_admin_permissions(), _build_requested_from_user)
    ),
    telemetry_payload: PatchUserTelemetryRequest = Body(...),
) -> list[GetUserResponse]:
    if user_to_change := UserUseCase().get_user_internal(filter=UserFilter(id=id)):
        check_privileges(user_to_change)
        return UserUseCase().patch_user_settings(user_id=id, configuration=telemetry_payload)
    raise NoUserFoundException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.patch(
    "/user/{id}/contact_info",
    status_code=status.HTTP_200_OK,
    description="Patch user contact info",
    tags=tags,
    response_model=GetUserResponse,
    response_model_exclude_unset=True,
)
def patch_user_contact_info(
    id: str = Depends(verify_object_id),
    check_privileges: Callable[..., None] = Depends(
        PrivilegesChecker(get_admin_permissions(), _build_requested_from_user)
    ),
    contact_info_payload: PatchUserContactInfoRequest = Body(...),
) -> list[GetUserResponse]:
    if user_to_change := UserUseCase().get_user_internal(filter=UserFilter(id=id)):
        check_privileges(user_to_change)
        return UserUseCase().patch_user_settings(user_id=id, configuration=contact_info_payload)
    raise NoUserFoundException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.delete(
    "/user",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete user",
    tags=tags,
    response_model=None,
)
def delete_user(
    id: Optional[str] = None,
    username: Optional[str] = None,
    check_privileges: Callable[..., None] = Depends(
        PrivilegesChecker(get_admin_permissions(), _build_requested_from_user)
    ),
    notifications: NotificationPort = Depends(get_notifications),
) -> None:
    filter = UserFilter(id=id, username=username)
    if user_to_change := UserUseCase().get_user_internal(filter=filter):
        check_privileges(user_to_change)
        UserUseCase().delete_user(filter=filter, notifications=notifications)
        return None
    raise NoUserFoundException(status_code=status.HTTP_404_NOT_FOUND)


user_router = {"router": api_router, "tags": tags}
