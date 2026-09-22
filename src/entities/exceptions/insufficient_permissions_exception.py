from fastapi import status

from entities.enum import AppErrorCodeEnum
from entities.exceptions.app_exception import AppException


class InsufficientPermissionsException(AppException):

    error_code = AppErrorCodeEnum.INSUFFICIENT_PERMISSIONS

    def __init__(self, internal: str = None, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_403_FORBIDDEN,
            internal=internal,
            **kwargs,
        )

    def __str__(self):
        return "You don't have access to this resource"
