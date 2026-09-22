import os

import mongomock
import pytest
from fastapi.testclient import TestClient

os.environ.update(
    {
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DATABASE_NAME": "iam_scenarios",
        "AUTH_SECRET_KEY": "scenario-secret",
        "AUTH_ALGORITHM": "HS256",
        "MFA_SECRET_KEY": "scenario-mfa-secret",
        "EXPIRATION_MFA_OTP_CODE_IN_SECONDS": "30",
        "API_URL": "http://iam.test",
        "APP_CLIENT_URL": "http://localhost:3000",
        "CORS_ALLOWED_ORIGINS": "http://localhost:3000",
        "API_VERSION": "",
        "TRACKING_LOG_PII": "false",
    }
)

from infra.database import mongo_database
from main import app
from presentation.dependencies.notification_service import get_notifications


class RecordingNotifications:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        self.sent.append(notification)

    def of_kind(self, kind):
        return [item for item in self.sent if item.payload.get("kind") == kind]

    def of_event(self, event_type):
        return [item for item in self.sent if item.payload.get("event_type") == event_type]


@pytest.fixture
def notifications():
    return RecordingNotifications()


@pytest.fixture
def client(notifications, monkeypatch):
    mongo = mongomock.MongoClient()
    monkeypatch.setattr(mongo_database, "get_client", lambda: mongo)
    monkeypatch.setattr(mongo_database, "_mongo_client", None)
    app.dependency_overrides[get_notifications] = lambda: notifications
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
