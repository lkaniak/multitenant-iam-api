from entities.enum.errors_enum import ValidationErrorCodeEnum
from entities.exceptions.app_exception import AppException


class OrganizationUserGroupNonexistentException(AppException):
    error_code: ValidationErrorCodeEnum = (
        ValidationErrorCodeEnum.ORGANIZATION_USER_GROUP_NONEXISTENT
    )

    def __init__(self, **kwargs):
        super().__init__(error_code=self.error_code.value, **kwargs)

    def __str__(self):
        return "Organization user group does not exist"
