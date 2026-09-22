from typing import Optional

from fastapi import status

from entities.enum.errors_enum import AppErrorCodeEnum, ValidationErrorCodeEnum
from entities.exceptions.app_exception import AppException


class MultipleOwnersInOrganizationException(AppException):

    error_code: AppErrorCodeEnum = AppErrorCodeEnum.MULTIPLE_OWNERS_IN_ORGANIZATION

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return "Multiple owners in organization"


class OrganizationNameAlreadyExistsException(AppException):

    error_code: ValidationErrorCodeEnum = ValidationErrorCodeEnum.ORGANIZATION_NAME_ALREADY_EXISTS

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return "Organization name already exists"


class OrganizationNonexistentException(AppException):

    error_code: ValidationErrorCodeEnum = ValidationErrorCodeEnum.ORGANIZATION_NONEXISTENT

    def __init__(self, status_code: Optional[int] = None, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status_code if status_code else status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return "Organization does not exist"


class OrganizationInactiveException(AppException):

    error_code: AppErrorCodeEnum = AppErrorCodeEnum.ORGANIZATION_INACTIVE

    def __init__(self, **kwargs):
        super().__init__(error_code=self.error_code.value, **kwargs)

    def __str__(self):
        return "Organization is inactive"


class InvalidSettingsForOrganizationException(AppException):

    error_code: AppErrorCodeEnum = AppErrorCodeEnum.ORGANIZATION_INVALID_SETTINGS

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            **kwargs,
        )

    def __str__(self):
        return "Invalid settings for organization. Could not create."


class OrganizationInformationAlreadyExistsException(AppException):

    error_code: AppErrorCodeEnum = AppErrorCodeEnum.ORGANIZATION_INFORMATION_ALREADY_EXISTS

    def __init__(self, already_exists_dict: dict, **kwargs):
        information_already_exists_str = "Information that already exists: " + ", ".join(
            already_exists_dict.keys()
        )
        super().__init__(
            error_code=self.error_code.value, internal=information_already_exists_str, **kwargs
        )

    def __str__(self):
        return "Organization information already exists"


class OrganizationCreatedButErrorNotifyingException(AppException):

    error_code: AppErrorCodeEnum = AppErrorCodeEnum.ORGANIZATION_CREATED_BUT_ERROR_NOTIFICATIONS

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            **kwargs,
        )

    def __str__(self):
        return "Organization created but there was an error sending the welcome email"


class InvalidOrganizationPreferencesException(AppException):

    error_code: ValidationErrorCodeEnum = ValidationErrorCodeEnum.ORGANIZATION_PREFERENCE_IS_INVALID

    def __init__(self, invalid_field: str, **kwargs):
        self.invalid_field = invalid_field

        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return f"Organization preference is invalid. Please check the {self.invalid_field} field value."


class InvalidOrganizationException(AppException):

    error_code: ValidationErrorCodeEnum = ValidationErrorCodeEnum.ORGANIZATION_IS_INVALID

    def __init__(self, **kwargs):

        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs,
        )

    def __str__(self):
        return "Invalid Organization."
