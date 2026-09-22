from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AlertChannelEntity(BaseModel):
    id: str = Field("", description="Channel id")
    type: str = Field(..., description="Channel type")
    destination: str = Field(..., description="Delivery destination")
    enabled: bool = Field(True, description="Whether the channel is active")


class AlertEntity(BaseModel):
    id: str = Field("", description="Alert id")
    organization_id: str = Field(..., description="Organization id")
    name: str = Field(..., description="Alert name")
    event_type: str = Field(..., description="IAM event that triggers the alert")
    enabled: bool = Field(True, description="Whether the alert is active")
    channels: list[AlertChannelEntity] = Field(
        default_factory=list, description="Delivery channels"
    )
    created_at: datetime = Field(..., description="Alert creation date")
    updated_at: datetime = Field(..., description="Alert update date")

    @field_validator("organization_id", mode="before")
    def validate_organization_id(cls, value):
        return str(value)
