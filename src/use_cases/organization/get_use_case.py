from entities.exceptions.invalid_filter_exception import InvalidFilterRequiredException
from infra.repositories.organization_repository import OrganizationRepository
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.response.organization.get_organization_response import (
    GetOrganizationResponse,
    GetListOrganizationResponse,
)


@classmethod
def get_organization(cls, filter: OrganizationFilter) -> GetOrganizationResponse:
    if not any(filter.model_dump().values()):
        raise InvalidFilterRequiredException()
    organization_entity = OrganizationRepository().get_organization(filter=filter)
    return (
        GetOrganizationResponse(**organization_entity.model_dump()) if organization_entity else None
    )


@classmethod
def get_organizations(cls) -> list[GetOrganizationResponse]:
    organizations = OrganizationRepository().get_organizations()
    return [
        GetListOrganizationResponse(**organization.model_dump()) for organization in organizations
    ]


@classmethod
def get_first_organization(cls) -> GetOrganizationResponse:
    organization = OrganizationRepository().get_first_organization()
    return GetOrganizationResponse(**organization.model_dump())
