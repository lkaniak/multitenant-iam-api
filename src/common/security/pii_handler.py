import json
import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

REDACTED = "[REDACTED]"
PII_KEYS = {
    "password",
    "old_password",
    "new_password",
    "temporary_password",
    "email",
    "first_name",
    "last_name",
    "phone",
    "username",
    "token",
    "access_token",
    "authorization",
    "temporary_otp_code",
    "otp",
    "secret",
    "key",
    "destination",
}
PII_HEADERS = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-auth-token",
}
PII_QUERY_KEYS = {
    "email",
    "password",
    "token",
    "username",
    "phone",
    "access_token",
}
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


def redact_string(value: str) -> str:
    redacted = EMAIL_PATTERN.sub(REDACTED, value)
    return JWT_PATTERN.sub(REDACTED, redacted)


def redact_data(value):
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if str(key).lower() == "user_id":
                redacted[key] = item
            elif str(key).lower() in PII_KEYS:
                redacted[key] = REDACTED
            else:
                redacted[key] = redact_data(item)
        return redacted
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, str):
        return redact_string(value)
    return value


def redact_headers(headers) -> dict:
    redacted = {}
    for key, value in headers.items():
        if key.lower() in PII_HEADERS:
            if key.lower() == "authorization" and value:
                scheme = value.split()[0] if " " in value else "Bearer"
                redacted[key] = f"{scheme} {REDACTED}"
            else:
                redacted[key] = REDACTED
        else:
            redacted[key] = redact_string(value)
    return redacted


def redact_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return redact_string(url)
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in PII_QUERY_KEYS:
            query.append((key, REDACTED))
        else:
            query.append((key, redact_string(value)))
    return urlunparse(parsed._replace(query=urlencode(query)))


def redact_body(body: str, content_type: str) -> str:
    if not body:
        return ""
    if content_type.startswith("multipart/"):
        return "[REDACTED MULTIPART]"
    try:
        parsed = json.loads(body)
        return json.dumps(redact_data(parsed), default=str)
    except (json.JSONDecodeError, TypeError):
        pass
    if "application/x-www-form-urlencoded" in content_type:
        query = []
        for key, value in parse_qsl(body, keep_blank_values=True):
            if key.lower() in PII_KEYS or key.lower() in PII_QUERY_KEYS:
                query.append((key, REDACTED))
            else:
                query.append((key, redact_string(value)))
        return urlencode(query)
    return redact_string(body)
