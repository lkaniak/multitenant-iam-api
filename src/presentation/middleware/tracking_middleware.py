import jwt
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from common.security.pii_handler import redact_body, redact_headers, redact_url
from config import settings


def _extract_user_id(authorization: str | None) -> str | None:
    if not authorization:
        return None
    token = authorization.split()[-1]
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET_KEY,
            algorithms=settings.AUTH_ALGORITHM,
            options={"verify_aud": False, "verify_exp": False},
        )
        return payload.get("sub")
    except jwt.PyJWTError:
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("sub")
        except jwt.PyJWTError:
            return None


class TrackingRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        raw_body = body.decode(errors="replace")
        authorization = request.headers.get("authorization")
        user_id = _extract_user_id(authorization)

        if settings.TRACKING_LOG_PII:
            url = str(request.url)
            headers = dict(request.headers)
            logged_body = raw_body
        else:
            url = redact_url(str(request.url))
            headers = redact_headers(request.headers)
            logged_body = redact_body(raw_body, request.headers.get("content-type", "").lower())

        logger.info(
            f"""
                Request details:
                - User ID: {user_id or "-"}
                - URL: {url}
                - Headers: {headers}
                - Method: {request.method}
                - Body: {logged_body}
            """
        )

        async def receive():
            return {"type": "http.request", "body": body}

        request = Request(request.scope, receive=receive)

        return await call_next(request)
