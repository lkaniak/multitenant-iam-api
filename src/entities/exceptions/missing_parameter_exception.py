from typing import Optional

from entities.enum import ValidationErrorCodeEnum
from entities.exceptions.app_exception import AppException


class MissingParameterException(AppException):

    error_code = ValidationErrorCodeEnum.MISSING_PARAMETER

    def __init__(self, which_parameter: Optional[str] = None, **kwargs):
        self.which_parameter = which_parameter
        super().__init__(error_code=self.error_code.value, **kwargs)

    def __str__(self):
        return f"Missing Parameters{': ' + self.which_parameter if self.which_parameter else ''}"
