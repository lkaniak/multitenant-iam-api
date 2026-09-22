from infra.repositories.organization_repository import OrganizationRepository
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.request.organization.patch_organization_requests import (
    PatchOrganizationRequest,
)
from presentation.response.organization.get_organization_response import GetOrganizationResponse


@classmethod
def patch_organization(cls, organization: PatchOrganizationRequest) -> GetOrganizationResponse:
    patch_payload = cls.get_organization(filter=OrganizationFilter(id=organization.id)).model_dump(
        exclude={"id"}
    )
    patch_payload.update(organization.model_dump(exclude={"id"}))
    organization_entity = OrganizationRepository().patch_organization(
        organization_id=organization.id, patch_organization=patch_payload
    )
    return GetOrganizationResponse(**organization_entity.model_dump())
