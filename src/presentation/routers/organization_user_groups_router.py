from fastapi import APIRouter, Body, Depends, status

from common.security.permission_handler import (
    get_restricted_permissions,
)
from entities import UserEntity
from presentation.middleware.auth import RoleAndTypeChecker
from presentation.request.organization_user_groups.create_organization_user_groups_request import (
    CreateOrganizationUserGroupsRequest,
)
from presentation.request.organization_user_groups.edit_organization_user_group_request import (
    EditOrganizationUserGroupRequest,
    EditOrganizationUserGroupRequestFields,
)
from presentation.response.organization_user_groups.get_organization_user_groups_response import (
    GetOrganizationUserGroupResponse,
    GetOrganizationUserGroupsResponse,
)
from presentation.middleware.verify_object_id import verify_object_id
from use_cases.organization_user_groups import OrganizationUserGroupsUseCase

api_router = APIRouter()
tags = ["Organization User Groups"]


@api_router.post(
    "/user_groups",
    status_code=status.HTTP_201_CREATED,
    description="Create an organization user group",
    tags=tags,
    response_model=GetOrganizationUserGroupResponse,
    response_model_exclude_unset=True,
)
def create_organization_user_group(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
    group_payload: CreateOrganizationUserGroupsRequest = Body(...),
) -> GetOrganizationUserGroupResponse:
    return OrganizationUserGroupsUseCase().create_organization_user_group(
        group_payload=group_payload
    )


@api_router.get(
    "/user_groups",
    status_code=status.HTTP_200_OK,
    description="Get organization user groups",
    tags=tags,
    response_model=list[GetOrganizationUserGroupsResponse],
    response_model_exclude_unset=True,
)
def get_organization_user_groups(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
) -> list[GetOrganizationUserGroupsResponse]:
    return OrganizationUserGroupsUseCase().get_organization_user_groups()


@api_router.put(
    "/user_groups/{id}",
    status_code=status.HTTP_200_OK,
    description="Update an organization user group",
    tags=tags,
    response_model=GetOrganizationUserGroupResponse,
    response_model_exclude_unset=True,
)
def update_organization_user_group(
    id: str = Depends(verify_object_id),
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
    group_payload: EditOrganizationUserGroupRequestFields = Body(...),
) -> GetOrganizationUserGroupResponse:
    return OrganizationUserGroupsUseCase().edit_organization_user_group(
        group_payload=EditOrganizationUserGroupRequest(id=id, **group_payload.model_dump())
    )


@api_router.delete(
    "/user_groups/{id}",
    status_code=status.HTTP_200_OK,
    description="Delete an organization user group",
    tags=tags,
    response_model=None,
)
def delete_organization_user_group(
    id: str = Depends(verify_object_id),
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_restricted_permissions())
    ),
) -> None:
    return OrganizationUserGroupsUseCase().delete_organization_user_group(group_id=id)


organization_user_groups_router = {"router": api_router, "tags": tags}
