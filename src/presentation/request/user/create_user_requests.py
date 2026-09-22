from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from entities.enum.role_enum import RoleEnum
from entities.enum.user_type_enum import UserTypeEnum
from entities.exceptions.app_exception import AppException
from entities import AffiliationTypeEnum, ActivityAreaEnum, JobPositionEnum
from entities.exceptions.organization_exceptions import OrganizationNonexistentException
from entities.exceptions.invalid_id_exception import InvalidIdException
from entities.exceptions.invalid_parameter_exception import InvalidParameterException
from entities.exceptions.missing_parameter_exception import MissingParameterException
from entities.exceptions.multiple_exception import MultipleExceptions
from entities.exceptions.user_exceptions import (
    PasswordIsInvalidException,
    UsernameAlreadyExistsException,
)
from entities.pydantic_entity import BaseModelExtended
from use_cases.auth.authorization_use_case import AuthorizationUseCase


class UserSettingsRequest(BaseModelExtended):
    inactive: bool = Field(False, description="User is inactive")


class UserTelemetryRequest(BaseModelExtended):
    created_at: datetime = Field(datetime.now(), description="User created at")
    last_access_date: datetime = Field(None, description="User last access date")
    registration_origin: str = Field(None, description="User registration origin")
    first_access_user: bool = Field(False, description="First access user")


class UserContactInfoRequest(BaseModelExtended):
    first_name: str = Field("", description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    email: str = Field("", description="User email")
    job_position: Optional[JobPositionEnum] = Field(None, description="User job position")
    activity_area: Optional[ActivityAreaEnum] = Field(None, description="User activity area")
    phone: Optional[str] = Field(None, description="User phone")
    affiliation_type: Optional[AffiliationTypeEnum] = Field(
        None, description="User affiliation type"
    )

    class Config:
        use_enum_values = True


class CreateUserRequest(BaseModelExtended):
    organization_id: Optional[str] = Field(
        None, description="Organization id the user is associated to"
    )
    username: str = Field(..., description="User username")
    password: str = Field(..., description="Encrypted user password")
    role: str = Field(..., description="User role")
    user_type: str = Field(..., description="User type")
    contact_info: UserContactInfoRequest = Field(
        default_factory=UserContactInfoRequest, description="user contact info"
    )
    telemetry: UserTelemetryRequest = Field(
        default_factory=UserTelemetryRequest, description="User telemetry info"
    )
    settings: UserSettingsRequest = Field(
        default_factory=UserSettingsRequest, description="User configuration"
    )

    @model_validator(mode="before")
    def model_validate(self):
        password = self.get("password", "")
        organization_id = self.get("organization_id", "")
        role = self.get("role", "")
        user_type = self.get("user_type", "")
        username = self.get("username", "")
        contact_info_raw = self.get("contact_info", {})
        if isinstance(contact_info_raw, BaseModel):
            contact_info_payload = contact_info_raw.model_dump()
        else:
            contact_info_payload = contact_info_raw if isinstance(contact_info_raw, dict) else {}
        valid_roles = [member.value for member in RoleEnum]
        valid_user_types = [member.value for member in UserTypeEnum]
        exceptions: list[AppException] = []

        if not role:
            exceptions.append(MissingParameterException(which_parameter="role"))

        if not user_type:
            exceptions.append(MissingParameterException(which_parameter="user_type"))

        if not organization_id and user_type != UserTypeEnum.SYSTEM_ADMIN.value:
            exceptions.append(MissingParameterException(which_parameter="organization_id"))

        if organization_id:
            if not AuthorizationUseCase.organization_id_exists(organization_id=organization_id):
                exceptions.append(OrganizationNonexistentException())
            if not ObjectId.is_valid(organization_id):
                exceptions.append(InvalidIdException())

        if role not in valid_roles:
            exceptions.append(
                InvalidParameterException(which_parameter="role", correction=",".join(valid_roles))
            )

        if user_type not in valid_user_types:
            exceptions.append(
                InvalidParameterException(
                    which_parameter="user_type", correction=",".join(valid_user_types)
                )
            )

        if not username:
            exceptions.append(MissingParameterException(which_parameter="username"))

        if AuthorizationUseCase.username_exists(username=username):
            exceptions.append(UsernameAlreadyExistsException())

        if invalid_reasons := AuthorizationUseCase.password_invalid(password=password):
            exceptions.extend(
                [PasswordIsInvalidException(reason=reason) for reason in invalid_reasons]
            )

        if invalid_reasons := AuthorizationUseCase.check_contact_info_is_valid(
            user_type=user_type, contact_info=contact_info_payload
        ):
            exceptions.extend(
                [
                    InvalidParameterException(
                        which_parameter=reason[0], correction=",".join(reason[1])
                    )
                    for reason in invalid_reasons
                ]
            )

        if exception := MultipleExceptions.handle_multiple_exceptions(exceptions=exceptions):
            raise exception
        return self


class CreateUsersRequest(BaseModel):

    users: list[CreateUserRequest]
