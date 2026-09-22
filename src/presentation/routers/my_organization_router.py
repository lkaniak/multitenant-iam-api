from fastapi import APIRouter, Body, Depends, status

from common.security.permission_handler import get_owner_permissions, get_all_permissions
from entities import UserEntity
from entities.exceptions.organization_exceptions import OrganizationNonexistentException
from presentation.middleware.auth import RoleAndTypeChecker
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.request.organization.patch_organization_requests import (
    PatchOrganizationRequest,
    PatchMyOrganizationRequest,
)
from presentation.response.organization.get_organization_response import GetOrganizationResponse
from presentation.response.user.get_user_response import GetUserResponse
from use_cases.organization import OrganizationUseCase
from use_cases.user import UserUseCase

api_router = APIRouter()
tags = ["Organization"]


@api_router.get(
    "/my/organization/users",
    status_code=status.HTTP_200_OK,
    description="Get my organization users",
    tags=tags + ["my"],
    response_model=list[GetUserResponse],
    response_model_exclude_unset=True,
)
def get_my_organization_users(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_all_permissions())
    ),
) -> list[GetUserResponse]:
    return UserUseCase().get_organization_users_without_owner(
        organization_id=logged_user.organization_id
    )


@api_router.get(
    "/my/organization",
    status_code=status.HTTP_200_OK,
    description="Get my organization",
    tags=tags + ["my"],
    response_model=GetOrganizationResponse,
    response_model_exclude_unset=True,
)
def get_my_organization(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_all_permissions())
    ),
) -> GetOrganizationResponse:
    if organization := OrganizationUseCase().get_organization(
        OrganizationFilter(id=logged_user.organization_id)
    ):
        return organization
    raise OrganizationNonexistentException(status_code=status.HTTP_404_NOT_FOUND)


@api_router.patch(
    "/my/organization",
    status_code=status.HTTP_200_OK,
    description="Patch my organization",
    tags=tags + ["my"],
    response_model=GetOrganizationResponse,
    response_model_exclude_unset=True,
)
def patch_my_organization(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_owner_permissions())
    ),
    organization_payload: PatchMyOrganizationRequest = Body(...),
) -> list[GetOrganizationResponse]:
    if organization := OrganizationUseCase().get_organization(
        OrganizationFilter(id=logged_user.organization_id)
    ):
        return OrganizationUseCase().patch_organization(
            organization=PatchOrganizationRequest(
                id=organization.id, **organization_payload.model_dump()
            )
        )
    raise OrganizationNonexistentException(status_code=status.HTTP_404_NOT_FOUND)


my_organization_router = {"router": api_router, "tags": tags}
