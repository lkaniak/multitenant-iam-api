from presentation.request.base_filter import BaseFilter
from typing import Optional

from pydantic import Field


class OrganizationUserGroupsFilter(BaseFilter):
    id: Optional[str] = Field(None, description="Group id")
    organization_id: Optional[str] = Field(None, description="Group organization id")
    user_id: Optional[str] = Field(None, description="User id")
