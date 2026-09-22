from typing import Optional

from pydantic import Field

from entities import UserContactInfoEntity, UserSettingsEntity
from entities.enum import RoleEnum
from entities.pydantic_entity import BaseModelExtended
from entities.user_entity import UserTelemetryEntity
from presentation.response.organization.get_organization_response import GetMyOrganizationResponse


class GetUserResponse(BaseModelExtended):
    id: str = Field("", description="User id")
    organization_id: Optional[str] = Field(
        None, description="Organization id the user is associated to"
    )
    username: str = Field("", description="User username")
    role: str = Field(RoleEnum.REGULAR.value, description="User role")
    contact_info: UserContactInfoEntity = Field(
        default_factory=UserContactInfoEntity, description="user contact info"
    )
    settings: UserSettingsEntity = Field(
        default_factory=UserSettingsEntity, description="User configuration"
    )


class GetUsersResponse(BaseModelExtended):
    id: str = Field("", description="User id")
    name: str = Field("", description="User name")
    email: str = Field("", description="User email")
    role: str = Field(RoleEnum.REGULAR.value, description="User role")
    organization_id: Optional[str] = Field(
        "", description="Organization id the user is associated to"
    )
    organization_name: Optional[str] = Field(
        "", description="Organization name the user is associated to"
    )


class GetMyUserResponse(BaseModelExtended):
    id: str = Field("", description="User id")
    organization: Optional[GetMyOrganizationResponse] = Field(
        default_factory=GetMyOrganizationResponse, description="User organization"
    )
    username: str = Field("", description="User username")
    role: str = Field(RoleEnum.REGULAR.value, description="User role")
    user_type: Optional[str] = Field(None, description="User type")
    contact_info: UserContactInfoEntity = Field(
        default_factory=UserContactInfoEntity, description="user contact info"
    )
    settings: UserSettingsEntity = Field(
        default_factory=UserSettingsEntity, description="User configuration"
    )
    telemetry: UserTelemetryEntity = Field(
        default_factory=UserTelemetryEntity, description="User telemetry"
    )
