from fastapi import status

from entities.enum.errors_enum import AppErrorCodeEnum, ValidationErrorCodeEnum
from entities.exceptions.app_exception import AppException


class FailedNotifyNewUserException(AppException):

    error_code = AppErrorCodeEnum.FAILED_NOTIFY_NEW_USER

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            **kwargs,
        )


class NoUserFoundException(AppException):

    error_code = AppErrorCodeEnum.NO_USER_FOUND

    def __init__(self, **kwargs):
        super().__init__(error_code=self.error_code.value, internal="User was not found", **kwargs)


class IncorrectPassphraseException(AppException):

    error_code = AppErrorCodeEnum.INCORRECT_PASSPHRASE

    def __init__(self, **kwargs):
        super().__init__(error_code=self.error_code.value, **kwargs)

    def __str__(self):
        return "Incorrect credentials supplied"


class UserInactiveException(AppException):

    error_code = AppErrorCodeEnum.USER_INACTIVE

    def __init__(self, **kwargs):
        super().__init__(error_code=self.error_code.value, **kwargs)

    def __str__(self):
        return "User is inactive"


class UsernameAlreadyExistsException(AppException):

    error_code = ValidationErrorCodeEnum.USERNAME_ALREADY_EXISTS

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return "Username already exists"


class PasswordIsInvalidException(AppException):
    def __init__(self, reason: ValidationErrorCodeEnum, **kwargs):
        super().__init__(
            error_code=reason.value, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, **kwargs
        )

    def __str__(self):
        return "Password is invalid"


class EmailIsInvalidException(AppException):

    error_code = ValidationErrorCodeEnum.EMAIL_IS_INVALID

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return "Email is invalid"


class OwnerUsernameIsInvalidException(AppException):

    error_code = ValidationErrorCodeEnum.OWNER_USERNAME_INVALID

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )

    def __str__(self):
        return "Owner username is invalid"


class ErrorSendingResetPasswordRequestException(AppException):

    error_code = AppErrorCodeEnum.ERROR_SENDING_RESET_PASSWORD_REQUEST

    def __init__(self, **kwargs):
        super().__init__(
            error_code=self.error_code.value,
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            **kwargs,
        )

    def __str__(self):
        return "Error sending reset password request"
