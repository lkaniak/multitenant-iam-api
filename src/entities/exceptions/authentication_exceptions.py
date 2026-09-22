from entities.enum.errors_enum import AppErrorCodeEnum
from entities.exceptions.app_exception import AppException
from fastapi import status


class FailedToSendMfaOtpCodeException(AppException):

    error_code = AppErrorCodeEnum.MFA_OTP_CODE_SEND_FAILED

    def __init__(self, **kwargs):
        super().__init__(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            error_code=self.error_code.value,
            quiet=True,
            internal="Failed to send MFA otp code",
            **kwargs,
        )


class MfaOtpCodeExpiredException(AppException):

    error_code = AppErrorCodeEnum.MFA_OTP_CODE_EXPIRED

    def __init__(self, **kwargs):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, error_code=self.error_code.value, **kwargs
        )

    def __str__(self):
        return "The MFA otp code has expired. Please request a new code."


class MfaOtpCodeInvalidException(AppException):

    error_code = AppErrorCodeEnum.MFA_OTP_CODE_INVALID

    def __init__(self, **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=self.error_code.value,
            internal="MFA otp code is not valid",
            **kwargs,
        )

        def __str__(self):
            return "Credentials are invalid"
