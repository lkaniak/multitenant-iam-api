import os

os.environ.update(
    {
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DATABASE_NAME": "iam_coverage",
        "AUTH_SECRET_KEY": "coverage-secret",
        "AUTH_ALGORITHM": "HS256",
        "MFA_SECRET_KEY": "coverage-mfa-secret",
        "EXPIRATION_MFA_OTP_CODE_IN_SECONDS": "30",
        "API_URL": "http://iam.test",
        "APP_CLIENT_URL": "http://localhost:3000",
        "CORS_ALLOWED_ORIGINS": "",
        "API_VERSION": "",
        "TRACKING_LOG_PII": "false",
    }
)
