from typing import Optional

from fastapi import status

from entities.enum import ValidationErrorCodeEnum
from entities.exceptions.app_exception import AppException


class InvalidIdException(AppException):

    error_code = ValidationErrorCodeEnum.ID_IS_INVALID

    def __init__(self, which_parameter: Optional[str] = None, **kwargs):
        self.which_parameter = which_parameter
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return f"Invalid ID{': ' + self.which_parameter if self.which_parameter else ''}"
