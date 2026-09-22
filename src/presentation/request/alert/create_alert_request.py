from pydantic import BaseModel, Field

from entities.enum.alert_channel_type_enum import AlertChannelTypeEnum
from entities.enum.alert_event_type_enum import AlertEventTypeEnum


class AlertChannelRequest(BaseModel):
    type: AlertChannelTypeEnum = Field(..., description="Channel type")
    destination: str = Field(..., min_length=1, description="Delivery destination")
    enabled: bool = Field(True, description="Whether the channel is active")

    class Config:
        use_enum_values = True


class CreateAlertRequest(BaseModel):
    organization_id: str = Field(..., description="Organization id")
    name: str = Field(..., min_length=1, description="Alert name")
    event_type: AlertEventTypeEnum = Field(..., description="IAM event that triggers the alert")
    enabled: bool = Field(True, description="Whether the alert is active")
    channels: list[AlertChannelRequest] = Field(
        default_factory=list, description="Delivery channels"
    )

    class Config:
        use_enum_values = True
