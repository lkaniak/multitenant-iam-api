from typing import Optional

from fastapi import APIRouter, Body, Depends, status

from common.security.permission_handler import get_restricted_permissions
from entities import UserEntity
from entities.enum import RoleEnum
from entities.enum.organization_action_type_activity_enum import OrganizationActionTypeActivityEnum
from entities.enum.user_type_enum import UserTypeEnum
from entities.exceptions.organization_exceptions import OrganizationNonexistentException
from notification_service import NotificationPort

from presentation.dependencies.notification_service import get_notifications
from presentation.middleware.auth import RoleAndTypeChecker
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.request.organization.create_organization_request import CreateOrganizationRequest
from presentation.request.organization.patch_organization_requests import (
    PatchOrganizationOwnerRequest,
    PatchOrganizationRequest,
)
from presentation.response.organization.create_organization_response import (
    CreateOrganizationResponse,
)
from presentation.response.organization.get_organization_response import (
    GetOrganizationResponse,
    GetListOrganizationResponse,
)
from presentation.response.user.get_user_response import GetUserResponse
from use_cases.organization import OrganizationUseCase
from use_cases.user import UserUseCase

api_router = APIRouter()
tags = ["Organization"]


@api_router.post(
    "/organization",
    status_code=status.HTTP_201_CREATED,
    description="Create an organization",
    tags=tags,
    response_model=CreateOrganizationResponse,
    response_model_exclude_unset=True,
)
def create_organization(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
    organization_payload: CreateOrganizationRequest = Body(...),
    notifications: NotificationPort = Depends(get_notifications),
) -> CreateOrganizationResponse:
    return OrganizationUseCase().create_organization_with_first_user(
        create_request=organization_payload, notifications=notifications
    )


@api_router.get(
    "/organization",
    status_code=status.HTTP_200_OK,
    description="Get organization",
    tags=tags,
    response_model=GetOrganizationResponse,
    response_model_exclude_unset=True,
)
def get_organization(
    id: Optional[str] = None,
    name: Optional[str] = None,
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
) -> GetOrganizationResponse:
    filter = OrganizationFilter(id=id, name=name)
    organization = OrganizationUseCase().get_organization(filter=filter)
    if not organization:
        raise OrganizationNonexistentException(status_code=status.HTTP_404_NOT_FOUND)
    return organization


@api_router.get(
    "/organizations",
    status_code=status.HTTP_200_OK,
    description="Get organizations",
    tags=tags,
    response_model=list[GetListOrganizationResponse],
    response_model_exclude_unset=True,
)
def get_organizations(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
) -> list[GetOrganizationResponse]:
    return OrganizationUseCase().get_organizations()


@api_router.patch(
    "/organization",
    status_code=status.HTTP_200_OK,
    description="Patch organization",
    tags=tags,
    response_model=GetOrganizationResponse,
    response_model_exclude_unset=True,
)
def patch_organization(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
    organization_payload: PatchOrganizationRequest = Body(...),
) -> list[GetOrganizationResponse]:
    if OrganizationUseCase().get_organization(OrganizationFilter(id=organization_payload.id)):
        return OrganizationUseCase().patch_organization(organization=organization_payload)
    raise OrganizationNonexistentException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.patch(
    "/organization/owner",
    status_code=status.HTTP_200_OK,
    description="Patch organization owner",
    tags=tags,
    response_model=GetUserResponse,
)
def patch_organization_owner(
    owner_payload: PatchOrganizationOwnerRequest,
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
) -> GetUserResponse:
    return OrganizationUseCase().patch_organization_owner(owner_payload=owner_payload)


@api_router.delete(
    "/organization",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete organization",
    tags=tags,
    response_model=None,
)
def delete_organization(
    id: Optional[str] = None,
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(
            allowed_permission_combinations=[(RoleEnum.ADMIN, UserTypeEnum.SYSTEM_ADMIN)]
        )
    ),
) -> None:
    filter = OrganizationFilter(id=id)
    if organization := OrganizationUseCase().get_organization(filter=filter):
        OrganizationUseCase().delete_organization(organization_id=organization.id)
        return None
    raise OrganizationNonexistentException(status_code=status.HTTP_404_NOT_FOUND)


organization_router = {"router": api_router, "tags": tags}
