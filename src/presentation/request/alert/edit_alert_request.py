from typing import Optional

from pydantic import BaseModel, Field

from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from presentation.request.alert.create_alert_request import AlertChannelRequest


class EditAlertRequestFields(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Alert name")
    event_type: Optional[AlertEventTypeEnum] = Field(
        None, description="IAM event that triggers the alert"
    )
    enabled: Optional[bool] = Field(None, description="Whether the alert is active")
    channels: Optional[list[AlertChannelRequest]] = Field(None, description="Delivery channels")

    class Config:
        use_enum_values = True


class EditAlertRequest(EditAlertRequestFields):
    id: str = Field(..., description="Alert id")
