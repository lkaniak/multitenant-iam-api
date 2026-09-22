from pydantic import Field

from entities.pydantic_entity import BaseModelExtended


class OrganizationPreferencesEntity(BaseModelExtended):
    timezone: str = Field(..., description="Timezone")
    currency: str = Field(..., description="Currency")
    locale: str = Field(..., description="Locale")
