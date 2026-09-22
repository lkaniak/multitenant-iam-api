from fastapi import status

from entities.enum import AppErrorCodeEnum
from entities.exceptions.app_exception import AppException


class InvalidFilterRequiredException(AppException):

    error_code = AppErrorCodeEnum.INVALID_FILTER_REQUIRED

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return "Invalid Filter, at least one of the fields are required."
