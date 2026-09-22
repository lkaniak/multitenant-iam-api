from entities.exceptions.organization_user_group_exceptions import (
    OrganizationUserGroupNonexistentException,
)
from infra.repositories.organization_user_group_repository import OrganizationUserGroupRepository
from entities.organization_user_group_entity import OrganizationUserGroupEntity


@classmethod
def delete_organization_user_group(cls, group_id: str) -> OrganizationUserGroupEntity:
    organization_user_group_repository = OrganizationUserGroupRepository()
    current_group = organization_user_group_repository.get_group(group_id=group_id)
    if not current_group:
        raise OrganizationUserGroupNonexistentException()
    organization_user_group_repository.delete_group(group_id=group_id)
