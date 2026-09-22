from pydantic import Field

from entities.pydantic_entity import BaseModelExtended


class CreateOrganizationResponse(BaseModelExtended):
    organization_id: str = Field("", description="Organization id")
    organization_name: str = Field("", description="Organization name")
