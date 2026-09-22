from typing import Optional

from pydantic import Field

from presentation.request.base_filter import BaseFilter


class OrganizationFilter(BaseFilter):
    name: Optional[str] = Field(None, description="Organization name")
