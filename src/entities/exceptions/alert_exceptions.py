from fastapi import status

from entities.enum.errors_enum import ValidationErrorCodeEnum
from entities.exceptions.app_exception import AppException


class AlertNonexistentException(AppException):
    error_code: ValidationErrorCodeEnum = ValidationErrorCodeEnum.ALERT_NONEXISTENT

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs,
        )

    def __str__(self):
        return "Alert does not exist"
