from typing import Optional

from pydantic import Field, model_validator

from entities.enum import RoleEnum, UserTypeEnum
from entities.exceptions.app_exception import AppException
from entities.exceptions.invalid_parameter_exception import InvalidParameterException
from entities.exceptions.multiple_exception import MultipleExceptions
from presentation.request.base_filter import BaseFilter


class UserFilter(BaseFilter):
    username: Optional[str] = Field(None, description="user username")
    organization_id: Optional[str] = Field(
        None, description="Organization id the user is associated to"
    )
    role: Optional[str] = Field(None, description="User role")
    user_type: Optional[str] = Field(None, description="User type")
    exclude_sys_adm: Optional[bool] = Field(False, description="User is not system admin")

    @model_validator(mode="before")
    def model_validate(self):
        role = self.get("role", "")
        user_type = self.get("user_type", "")
        valid_roles = [member.value for member in RoleEnum]
        valid_user_types = [member.value for member in UserTypeEnum]
        exceptions: list[AppException] = []
        if user_type and user_type not in valid_user_types:
            exceptions.append(
                InvalidParameterException(
                    which_parameter="user_type", correction=",".join(valid_user_types)
                )
            )
        if role and role not in valid_roles:
            exceptions.append(
                InvalidParameterException(which_parameter="role", correction=",".join(valid_roles))
            )

        if exception := MultipleExceptions.handle_multiple_exceptions(exceptions=exceptions):
            raise exception
        return self
