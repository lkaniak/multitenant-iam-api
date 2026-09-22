from datetime import datetime
from entities.exceptions.organization_user_group_exceptions import (
    OrganizationUserGroupNonexistentException,
)
from infra.repositories.organization_user_group_repository import OrganizationUserGroupRepository
from entities.organization_user_group_entity import OrganizationUserGroupEntity
from presentation.request.organization_user_groups.edit_organization_user_group_request import (
    EditOrganizationUserGroupRequest,
)


@classmethod
def edit_organization_user_group(
    cls, group_payload: EditOrganizationUserGroupRequest
) -> OrganizationUserGroupEntity:

    organization_user_group_repository = OrganizationUserGroupRepository()
    current_group = organization_user_group_repository.get_group(group_id=group_payload.id)
    if not current_group:
        raise OrganizationUserGroupNonexistentException()

    edit_payload = current_group.model_dump(exclude={"id"})
    edit_payload.update(group_payload.model_dump(exclude={"id"}))
    edit_payload.update({"updated_at": datetime.now()})

    return organization_user_group_repository.edit_group(
        group_id=group_payload.id, edit_group=edit_payload
    )
