from common.security.pii_handler import redact_body, redact_headers, redact_url
from config import Settings


def test_redacts_json_headers_and_query():
    body = redact_body(
        '{"email":"ada@acme.test","password":"secret","note":"keep"}',
        "application/json",
    )
    assert "ada@acme.test" not in body
    assert "secret" not in body
    assert "keep" in body

    headers = redact_headers(
        {"authorization": "Bearer eyJaaa.bbb.ccc", "accept": "application/json"}
    )
    assert headers["authorization"] == "Bearer [REDACTED]"
    assert headers["accept"] == "application/json"

    url = redact_url("http://iam.test/user?email=ada@acme.test&id=1")
    assert "ada@acme.test" not in url
    assert "id=1" in url


def test_cors_origins_include_client_and_extras():
    settings = Settings(
        MONGO_URI="mongodb://localhost",
        MONGO_DATABASE_NAME="iam",
        AUTH_SECRET_KEY="k",
        AUTH_ALGORITHM="HS256",
        MFA_SECRET_KEY="m",
        EXPIRATION_MFA_OTP_CODE_IN_SECONDS=30,
        APP_CLIENT_URL="http://localhost:3000",
        API_URL="http://iam.test",
        CORS_ALLOWED_ORIGINS="http://admin.test, http://localhost:3000",
    )
    assert settings.cors_allowed_origins == [
        "http://admin.test",
        "http://localhost:3000",
    ]
