from typing import Optional

from fastapi import status

from entities.enum import AppErrorCodeEnum
from entities.exceptions.app_exception import AppException


class InvalidParameterException(AppException):

    error_code = AppErrorCodeEnum.INVALID_PARAMETER

    def __init__(
        self, which_parameter: Optional[str] = None, correction: Optional[str] = None, **kwargs
    ):
        self.which_parameter = which_parameter
        self.correction = correction
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        if self.which_parameter and self.correction:
            return f"Invalid Parameter: {self.which_parameter}, Input should be: {self.correction}"
        return "Invalid Parameters"
