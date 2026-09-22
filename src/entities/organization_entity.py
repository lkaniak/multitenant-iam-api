from pydantic import Field

from entities.pydantic_entity import BaseModelExtended


class OrganizationEntity(BaseModelExtended):
    id: str = Field("", description="Organization id")
    name: str = Field("", description="Organization name")
    created_at: str = Field("", description="Organization creation date")
    organization_plan: str = Field("", description="Organization plan")
    inactive: bool = Field(False, description="Organization is inactive")
    registration_origin: str = Field("", description="Organization registration origin")
