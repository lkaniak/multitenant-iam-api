from pydantic import BaseModel, Field
from typing import Optional


class CreateOrganizationUserGroupsRequest(BaseModel):
    organization_id: str = Field(..., description="First organization in the group id")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
