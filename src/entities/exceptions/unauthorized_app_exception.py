from entities.enum.errors_enum import AppErrorCodeEnum
from entities.exceptions.app_exception import AppException


class UnauthorizedAppException(AppException):

    error_code = AppErrorCodeEnum.UNAUTHORIZED_APP

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            quiet=True,
            internal="Unauthorized application requesting access",
            **kwargs,
        )
