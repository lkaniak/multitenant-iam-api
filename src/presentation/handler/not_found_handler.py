from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


async def not_found_error(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content="Invalid Request",
    )
