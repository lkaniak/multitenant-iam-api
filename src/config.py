from pydantic_settings import BaseSettings, SettingsConfigDict

APP_VERSION = "1.0.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_ignore_empty=True, extra="ignore")

    MONGO_URI: str
    MONGO_DATABASE_NAME: str
    MONGO_DATABASE_ORGANIZATION_COLLECTION: str = "organization_collection"
    MONGO_DATABASE_ORGANIZATION_USER_GROUP_COLLECTION: str = "organization_user_group_collection"
    MONGO_DATABASE_USER_COLLECTION: str = "user_collection"
    MONGO_DATABASE_ORGANIZATION_ACTIVITY_COLLECTION: str = "organization_activity_collection"
    MONGO_DATABASE_ALERT_COLLECTION: str = "alerts_collection"
    MONGO_DATABASE_ORGANIZATION_PREFERENCES_COLLECTION: str = "organization_preferences_collection"
    MONGO_DATABASE_CHANNEL_COLLECTION: str = "channel_collection"

    AUTH_SECRET_KEY: str
    AUTH_ALGORITHM: str
    MFA_SECRET_KEY: str
    EXPIRATION_MFA_OTP_CODE_IN_SECONDS: int

    APP_CLIENT_URL: str
    API_URL: str
    CORS_ALLOWED_ORIGINS: str = ""

    MIN_PASSWORD_LENGTH: int = 8

    API_VERSION: str = ""

    DEBUG: bool = False
    TRACKING_LOG_PII: bool = False

    @property
    def cors_allowed_origins(self) -> list[str]:
        origins = [
            origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
        ]
        client_url = self.APP_CLIENT_URL.strip() if self.APP_CLIENT_URL else ""
        if client_url and client_url not in origins:
            origins.append(client_url)
        return origins


settings = Settings()
