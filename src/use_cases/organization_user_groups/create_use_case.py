from datetime import datetime

from infra.repositories.organization_user_group_repository import OrganizationUserGroupRepository
from presentation.request.organization_user_groups.create_organization_user_groups_request import (
    CreateOrganizationUserGroupsRequest,
)
from entities.organization_user_group_entity import OrganizationUserGroupEntity
from presentation.response.organization_user_groups.get_organization_user_groups_response import (
    GetOrganizationUserGroupResponse,
)


@classmethod
def create_organization_user_group(
    cls, group_payload: CreateOrganizationUserGroupsRequest
) -> OrganizationUserGroupEntity:
    payload = OrganizationUserGroupEntity(
        id="",
        name=group_payload.name,
        description=group_payload.description,
        users=[],
        organizations=[group_payload.organization_id],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    response = OrganizationUserGroupRepository().create_group(group=payload)
    return GetOrganizationUserGroupResponse(**response.model_dump())
