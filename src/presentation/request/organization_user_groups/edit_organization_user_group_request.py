from typing import Optional
from pydantic import BaseModel, Field


class EditOrganizationUserGroupRequestFields(BaseModel):
    name: Optional[str] = Field("", description="Group name")
    description: Optional[str] = Field("", description="Group description")
    users: list[str] = Field([], description="Users in the group")
    organizations: list[str] = Field([], description="Organizations in the group")


class EditOrganizationUserGroupRequest(EditOrganizationUserGroupRequestFields):
    id: str = Field(..., description="Group id")
