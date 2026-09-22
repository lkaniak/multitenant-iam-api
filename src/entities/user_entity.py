from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from entities.pydantic_entity import BaseModelDefault
from entities.enum import (
    RoleEnum,
    UserTypeEnum,
    AffiliationTypeEnum,
    ActivityAreaEnum,
    JobPositionEnum,
)


class UserSettingsEntity(BaseModel):
    inactive: bool = Field(False, description="User is inactive")


class UserTelemetryEntity(BaseModel):
    created_at: datetime = Field(datetime.now(), description="User created at")
    last_access_date: Optional[datetime] = Field(None, description="User last access date")
    registration_origin: Optional[str] = Field(None, description="User registration origin")
    first_access_user: bool = Field(False, description="First access user")


class UserContactInfoEntity(BaseModel):
    first_name: str = Field("", description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    email: str = Field("", description="User email")
    job_position: JobPositionEnum = Field(
        JobPositionEnum.OTHER.value, description="User job position"
    )
    activity_area: ActivityAreaEnum = Field(
        ActivityAreaEnum.OTHER.value, description="User activity area"
    )
    phone: Optional[str] = Field(None, description="User phone")
    affiliation_type: AffiliationTypeEnum = Field(
        AffiliationTypeEnum.OTHER.value, description="User affiliation type"
    )

    class Config:
        use_enum_values = True


class UserEntity(BaseModelDefault):
    id: str = Field("", description="User id")
    organization_id: Optional[str] = Field(
        None, description="Organization id the user is associated to"
    )
    username: str = Field("", description="User username")
    password: str = Field("", description="Encrypted user password")
    role: str = Field(RoleEnum.REGULAR.value, description="User role")
    user_type: str = Field(UserTypeEnum.OTHER.value, description="User type")
    contact_info: UserContactInfoEntity = Field(
        default_factory=UserContactInfoEntity, description="user contact info"
    )
    telemetry: UserTelemetryEntity = Field(
        default_factory=UserTelemetryEntity, description="User telemetry info"
    )
    settings: UserSettingsEntity = Field(
        default_factory=UserSettingsEntity, description="User configuration"
    )

    @field_validator("organization_id", mode="before")
    def convert_organization_id_to_str(cls, organization_id):
        return str(organization_id) if organization_id else None

    @field_validator("id", mode="before")
    def convert_id_to_str(cls, id):
        return str(id)
