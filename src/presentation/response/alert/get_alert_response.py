from datetime import datetime

from pydantic import BaseModel, Field


class AlertChannelResponse(BaseModel):
    id: str = Field(..., description="Channel id")
    type: str = Field(..., description="Channel type")
    destination: str = Field(..., description="Delivery destination")
    enabled: bool = Field(..., description="Whether the channel is active")


class GetAlertResponse(BaseModel):
    id: str = Field(..., description="Alert id")
    organization_id: str = Field(..., description="Organization id")
    name: str = Field(..., description="Alert name")
    event_type: str = Field(..., description="IAM event that triggers the alert")
    enabled: bool = Field(..., description="Whether the alert is active")
    channels: list[AlertChannelResponse] = Field(..., description="Delivery channels")
    created_at: datetime = Field(..., description="Alert creation date")
    updated_at: datetime = Field(..., description="Alert update date")
