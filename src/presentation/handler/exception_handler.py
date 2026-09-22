from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from entities.exceptions.app_exception import AppException
from entities.exceptions.multiple_exception import MultipleExceptions


async def exception_handler(request: Request, exc: Union[Exception, AppException]):
    content = {}

    internal = ""
    if hasattr(exc, "internal") and exc.internal:
        internal = f"\nInternal message: {exc.internal}"

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if issubclass(exc.__class__, MultipleExceptions):
        content["error_codes"] = [
            {"error_code": error.error_code, "message": str(error)} for error in exc.exceptions
        ]
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif issubclass(exc.__class__, AppException):
        content["error_code"] = exc.error_code
        content["message"] = str(exc)
        content["details"] = exc.details if exc.details else ""
        status_code = exc.status_code

    if status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_424_FAILED_DEPENDENCY]:
        logger.error(f"Exception {exc} \nfor requests {request}{internal}")
    else:
        logger.warning(f"Exception {exc} \nfor requests {request}{internal}")

    return JSONResponse(
        status_code=status_code,
        content=content,
    )
