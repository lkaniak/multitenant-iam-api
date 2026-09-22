from typing import Optional

from bson import ObjectId
from pydantic import Field, field_validator

from entities.exceptions.invalid_id_exception import InvalidIdException
from presentation.request.base_filter import BaseFilter


class AlertFilter(BaseFilter):
    organization_id: Optional[str] = Field(None, description="Organization id")
    event_type: Optional[str] = Field(None, description="IAM event type")
    enabled: Optional[bool] = Field(None, description="Whether the alert is active")

    @field_validator("organization_id")
    def check_organization_id(cls, organization_id):
        if organization_id and not ObjectId.is_valid(organization_id):
            raise InvalidIdException(which_parameter="organization_id")
        return organization_id
