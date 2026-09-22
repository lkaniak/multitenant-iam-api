from typing import Optional

import pytz
from babel import Locale
from pydantic import BaseModel, Field, field_validator

from entities.enum.organization_plan_enum import OrganizationPlanEnum
from entities.exceptions import InvalidOrganizationPreferencesException
from entities import AffiliationTypeEnum, ActivityAreaEnum, JobPositionEnum
from entities.exceptions.invalid_parameter_exception import InvalidParameterException
from entities.exceptions.user_exceptions import (
    EmailIsInvalidException,
    OwnerUsernameIsInvalidException,
)
from use_cases.user.user_helpers import is_valid_organization_owner_name, is_valid_email


class CreateOrganizationRequest(BaseModel):

    organization_name: str = Field("", description="Organization name")
    organization_owner_first_name: str = Field("", description="Organization owner first name")
    organization_owner_last_name: str = Field("", description="Organization owner last name")
    organization_owner_email: str = Field("", description="Organization owner email")
    organization_owner_job_position: JobPositionEnum = Field(
        ..., description="Organization owner job position"
    )
    organization_owner_activity_area: ActivityAreaEnum = Field(
        ..., description="Organization owner activy area"
    )
    organization_owner_phone: Optional[str] = Field(None, description="Organization owner phone")
    organization_owner_affiliation_type: AffiliationTypeEnum = Field(
        ..., description="Organization owner affiliation type"
    )
    organization_user_name: str = Field("", description="Organization user name")
    organization_preference_timezone: str = Field(
        "", description="Organization timezone preference"
    )
    organization_preference_currency: str = Field(
        "", description="Organization currency preference"
    )
    organization_preference_locale: str = Field("", description="Organization locale preference")
    organization_plan: OrganizationPlanEnum = Field(..., description="Organization plan")

    @field_validator("organization_user_name")
    def validate_organization_user_name(cls, organization_user_name):
        if not is_valid_organization_owner_name(name=organization_user_name):
            raise OwnerUsernameIsInvalidException()
        return organization_user_name

    @field_validator("organization_owner_email")
    def validate_organization_owner_email(cls, email):
        if not is_valid_email(email=email):
            raise EmailIsInvalidException()
        return email

    @field_validator("organization_preference_timezone")
    def validate_timezone(cls, timezone):
        if not timezone or timezone not in pytz.all_timezones:
            raise InvalidOrganizationPreferencesException(invalid_field="timezone")
        return timezone

    @field_validator("organization_preference_currency")
    def validate_currency(cls, currency):
        if not currency or currency not in Locale("en", "US").currencies.keys():
            raise InvalidOrganizationPreferencesException(invalid_field="currency")
        return currency

    @field_validator("organization_preference_locale")
    def validate_locale(cls, locale):
        try:
            Locale.parse(locale)
            return locale
        except Exception:
            raise InvalidOrganizationPreferencesException(invalid_field="locale")

    @field_validator("organization_plan", mode="before")
    def validate_organization_plan(cls, organization_plan):
        valid_plans = [member.value for member in OrganizationPlanEnum]
        if not organization_plan or organization_plan not in valid_plans:
            raise InvalidParameterException(
                which_parameter="organization_plan",
                correction=",".join(valid_plans),
            )
        return OrganizationPlanEnum.from_str(organization_plan)

    class Config:
        use_enum_values = True
