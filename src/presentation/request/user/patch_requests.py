from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator, model_validator

from entities.enum.errors_enum import ValidationErrorCodeEnum
from entities.enum import RoleEnum, AffiliationTypeEnum, ActivityAreaEnum, JobPositionEnum
from entities.exceptions import AppException, InvalidParameterException, MultipleExceptions
from entities.exceptions.user_exceptions import (
    EmailIsInvalidException,
    PasswordIsInvalidException,
    UsernameAlreadyExistsException,
)
from entities.pydantic_entity import BaseModelDefault, BaseModelExtended
from use_cases.auth.authorization_use_case import AuthorizationUseCase
from use_cases.user.user_helpers import is_valid_email


class PatchUserSettingsRequest(BaseModelDefault):
    inactive: bool = Field(False, description="User is inactive")

    def __repr__(self) -> str:
        return "settings"


class PatchUserTelemetryRequest(BaseModelDefault):
    last_access_date: Optional[datetime] = Field(None, description="User last access date")
    first_access_user: Optional[bool] = Field(None, description="First access user")

    def __repr__(self) -> str:
        return "telemetry"


class PatchUserContactInfoRequest(BaseModelDefault):
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    email: Optional[str] = Field(None, description="User email")
    job_position: Optional[JobPositionEnum] = Field(None, description="User job position")
    activity_area: Optional[ActivityAreaEnum] = Field(None, description="User activity area")
    phone: Optional[str] = Field(None, description="User phone")
    affiliation_type: Optional[AffiliationTypeEnum] = Field(
        None, description="User affiliation type"
    )

    @model_validator(mode="before")
    def model_validate(self):
        exceptions: list[AppException] = []

        email = self.get("email", "")
        if email and not is_valid_email(email=email):
            exceptions.append(EmailIsInvalidException())

        if exception := MultipleExceptions.handle_multiple_exceptions(exceptions=exceptions):
            raise exception
        return self

    def __repr__(self) -> str:
        return "contact_info"

    class Config:
        use_enum_values = True


class PatchUserRequest(BaseModelExtended):
    id: str = Field(..., description="User id")
    username: Optional[str] = Field(None, description="User username")
    old_password: Optional[str] = Field(None, description="user old password")
    password: Optional[str] = Field(None, description="Encrypted user password")
    role: Optional[str] = Field(None, description="User role")
    contact_info: PatchUserContactInfoRequest = Field(
        default_factory=PatchUserContactInfoRequest, description="user contact info"
    )

    @model_validator(mode="before")
    def model_validate(self):
        user_id = self.get("id", "")
        password = self.get("password", "")
        old_password = self.get("old_password", "")
        role = self.get("role", "")
        username = self.get("username", "")
        valid_roles = [member.value for member in RoleEnum]
        exceptions: list[AppException] = []
        if role and role not in valid_roles:
            exceptions.append(
                InvalidParameterException(which_parameter="role", correction=",".join(valid_roles))
            )

        if AuthorizationUseCase.username_exists(username=username):
            exceptions.append(UsernameAlreadyExistsException())

        if password:
            invalid_reasons = AuthorizationUseCase.password_invalid(password=password)
            if old_password and not AuthorizationUseCase.password_matches_old(
                old_password, user_id=user_id
            ):
                invalid_reasons.append(ValidationErrorCodeEnum.OLD_PASSWORD_INCORRECT)
            if AuthorizationUseCase.password_matches_old(password, user_id=user_id):
                invalid_reasons.append(ValidationErrorCodeEnum.PASSWORD_ALREADY_USED)
            if invalid_reasons:
                exceptions.extend(
                    [PasswordIsInvalidException(reason=reason) for reason in invalid_reasons]
                )
        if exception := MultipleExceptions.handle_multiple_exceptions(exceptions=exceptions):
            raise exception
        return self


class PatchMyUserRequest(BaseModelExtended):
    old_password: Optional[str] = Field(None, description="user old password")
    new_password: Optional[str] = Field(None, description="user password")
    contact_info: PatchUserContactInfoRequest = Field(
        default_factory=PatchUserContactInfoRequest, description="user contact info"
    )


class ResetPasswordRequest(BaseModelDefault):
    username: str = Field(..., description="user username")

    @field_validator("username", mode="before")
    def lowercase_username(cls, username):
        return username.lower() if username else ""
