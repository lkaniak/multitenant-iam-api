from typing import Optional

from pydantic import Field, model_validator

from common.data.dictionary_handler import merge_defaults_with_target
from entities.enum.organization_plan_enum import OrganizationPlanEnum
from entities.exceptions.organization_exceptions import OrganizationNonexistentException
from entities.exceptions.invalid_parameter_exception import InvalidParameterException
from entities.pydantic_entity import BaseModelDefault, BaseModelExtended
from presentation.request.user.patch_requests import (
    PatchUserContactInfoRequest,
    PatchUserSettingsRequest,
)
from use_cases.auth.authorization_use_case import AuthorizationUseCase


class PatchOrganizationOwnerRequest(BaseModelDefault):
    organization_id: str = Field(..., description="Organization id")
    contact_info: PatchUserContactInfoRequest = Field(
        default_factory=PatchUserContactInfoRequest, description="user contact info"
    )
    settings: PatchUserSettingsRequest = Field(
        default_factory=PatchUserSettingsRequest, description="User configuration"
    )


class PatchOrganizationRequest(BaseModelExtended):
    id: str = Field(..., description="Organization id")
    name: Optional[str] = Field(None, description="Organization name")
    inactive: Optional[bool] = Field(None, description="Organization is inactive")
    organization_plan: Optional[str] = Field(None, description="Organization plan")

    @model_validator(mode="before")
    def model_validate(self):
        organization = AuthorizationUseCase.organization_id_exists(
            organization_id=self.get("id", "")
        )
        organization_plan = self.get("organization_plan", "")
        if not organization:
            raise OrganizationNonexistentException()

        if organization_plan:
            valid_plans = [member.value for member in OrganizationPlanEnum]
            if organization_plan not in valid_plans:
                raise InvalidParameterException(
                    which_parameter="organization_plan",
                    correction=",".join(valid_plans),
                )

        self = merge_defaults_with_target(
            self,
            previous_model=organization.model_dump(),
        )

        return self


class PatchMyOrganizationRequest(BaseModelExtended):
    name: Optional[str] = Field(None, description="Organization name")
