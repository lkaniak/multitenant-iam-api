from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel, field_validator


class OrganizationUserGroupEntity(BaseModel):
    id: str = Field(..., description="Group id")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field("", description="Group description")
    users: list[str] = Field([], description="Users in the group")
    organizations: list[str] = Field([], description="Organizations in the group")
    created_at: datetime = Field(..., description="Group creation date")
    updated_at: datetime = Field(..., description="Group update date")

    @field_validator("users", "organizations", mode="before")
    def convert_users_and_organizations_to_str(cls, value):
        return [str(id) for id in value]
