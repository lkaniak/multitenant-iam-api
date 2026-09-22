from loguru import logger

from infra.repositories import (
    AlertRepository,
    OrganizationActivityRepository,
    OrganizationPreferencesRepository,
    OrganizationRepository,
    OrganizationUserGroupRepository,
)
from presentation.request.user.user_filter_request import UserFilter
from use_cases.user import UserUseCase


def purge_organization(organization_id: str) -> None:
    OrganizationUserGroupRepository().remove_organization_from_groups(organization_id)
    logger.success(f"Removed organization {organization_id} from user groups")
    AlertRepository().delete_by_organization_id(organization_id)
    logger.success(f"Removed {organization_id} alerts")
    OrganizationPreferencesRepository().delete_by_organization_id(organization_id)
    logger.success(f"Removed {organization_id} preferences")
    OrganizationActivityRepository().delete_by_organization_id(organization_id)
    logger.success(f"Removed {organization_id} activities")


@classmethod
def delete_organization(cls, organization_id: str) -> None:
    result = OrganizationRepository().delete_organization_by_id(organization_id=organization_id)
    if result:
        UserUseCase().delete_user(filter=UserFilter(organization_id=organization_id))
        purge_organization(organization_id=organization_id)
