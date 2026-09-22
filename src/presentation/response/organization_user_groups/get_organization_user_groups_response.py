from typing import Optional

from pydantic import Field, BaseModel
from presentation.response.user.get_user_response import GetUsersResponse
from presentation.response.organization.get_organization_response import GetListOrganizationResponse
from datetime import datetime


class GetOrganizationUserGroupResponse(BaseModel):
    id: str = Field(..., description="Group id")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field("", description="Group description")
    users: list[str] = Field(..., description="Users in the group")
    organizations: list[str] = Field(..., description="Organizations in the group")
    created_at: datetime = Field(..., description="Group creation date")
    updated_at: datetime = Field(..., description="Group update date")


class GetOrganizationUserGroupsResponse(BaseModel):
    id: str = Field(..., description="Group id")
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field("", description="Group description")
    users: list[GetUsersResponse] = Field(..., description="Users in the group")
    organizations: list[GetListOrganizationResponse] = Field(
        ..., description="Organizations in the group"
    )
    created_at: datetime = Field(..., description="Group creation date")
    updated_at: datetime = Field(..., description="Group update date")


class GetMyUserGroupsOrganizationsResponse(BaseModel):
    organizations: list[GetListOrganizationResponse] = Field(
        ..., description="Organizations allowed for the user"
    )
