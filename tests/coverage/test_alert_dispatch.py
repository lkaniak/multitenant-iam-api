from datetime import datetime
from unittest.mock import patch

from bson import ObjectId

from entities.alert_entity import AlertChannelEntity, AlertEntity
from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from services.alert.alert_dispatch_service import AlertDispatchService


class Capture:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        self.sent.append(notification)


def _alert(organization_id):
    return AlertEntity(
        id=str(ObjectId()),
        organization_id=organization_id,
        name="Login failures",
        event_type=AlertEventTypeEnum.LOGIN_FAILED.value,
        enabled=True,
        channels=[
            AlertChannelEntity(type="email", destination="ops@acme.test", enabled=True),
            AlertChannelEntity(
                type="slack", destination="https://hooks.example/slack", enabled=True
            ),
            AlertChannelEntity(
                type="webhook", destination="https://hooks.example/disabled", enabled=False
            ),
        ],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@patch("services.alert.alert_dispatch_service.AlertRepository")
def test_dispatch_sends_enabled_channels_only(alert_repository):
    organization_id = str(ObjectId())
    alert_repository.return_value.get_alerts.return_value = [_alert(organization_id)]
    capture = Capture()
    AlertDispatchService(capture).dispatch(
        event_type=AlertEventTypeEnum.LOGIN_FAILED,
        organization_id=organization_id,
        data={"username": "ada"},
    )
    assert [item.channel for item in capture.sent] == ["email", "slack"]
    assert capture.sent[0].destination == "ops@acme.test"
    assert capture.sent[0].payload["data"]["username"] == "ada"
    assert "text" in capture.sent[1].payload
    assert "ada" not in capture.sent[1].payload["text"]


@patch("services.alert.alert_dispatch_service.AlertRepository")
def test_dispatch_skips_events_without_an_organization(alert_repository):
    capture = Capture()
    AlertDispatchService(capture).dispatch(
        event_type=AlertEventTypeEnum.USER_CREATED,
        organization_id=None,
    )
    alert_repository.assert_not_called()
    assert capture.sent == []
