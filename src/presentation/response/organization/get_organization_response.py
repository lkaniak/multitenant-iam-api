from pydantic import Field

from entities.pydantic_entity import BaseModelExtended


class GetOrganizationResponse(BaseModelExtended):
    id: str = Field("", description="Organization id")
    name: str = Field("", description="Organization name")
    registration_origin: str = Field("", description="Organization registration origin")
    inactive: bool = Field(False, description="Organization is inactive")


class GetListOrganizationResponse(BaseModelExtended):
    id: str = Field("", description="Organization id")
    name: str = Field("", description="Organization name")


class GetMyOrganizationResponse(BaseModelExtended):
    id: str = Field("", description="Organization id")
    name: str = Field("", description="Organization name")
    organization_plan: str = Field("", description="Organization plan")
