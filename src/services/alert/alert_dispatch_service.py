from datetime import datetime, timezone

from loguru import logger
from notification_service import Notification, NotificationPort

from entities.alert_entity import AlertChannelEntity, AlertEntity
from entities.enum.alert_channel_type_enum import AlertChannelTypeEnum
from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from infra.repositories.alert_repository import AlertRepository
from presentation.request.alert.alert_filter_request import AlertFilter


class AlertDispatchService:
    def __init__(self, notifications: NotificationPort):
        self.notifications = notifications

    def dispatch(
        self,
        event_type: AlertEventTypeEnum,
        organization_id: str | None,
        data: dict | None = None,
    ) -> None:
        if not organization_id:
            return
        try:
            alerts = AlertRepository().get_alerts(
                AlertFilter(
                    organization_id=organization_id,
                    event_type=event_type.value,
                    enabled=True,
                )
            )
        except Exception as exc:
            logger.error(f"Failed to load alerts for {event_type.value}. Error: {exc}")
            return
        occurred_at = datetime.now(timezone.utc).isoformat()
        for alert in alerts:
            payload = {
                "event_type": event_type.value,
                "organization_id": organization_id,
                "alert_id": alert.id,
                "alert_name": alert.name,
                "occurred_at": occurred_at,
                "data": data or {},
            }
            for channel in alert.channels:
                if channel.enabled:
                    self._deliver(alert, channel, payload)

    def _deliver(self, alert: AlertEntity, channel: AlertChannelEntity, payload: dict) -> None:
        body = dict(payload)
        if channel.type == AlertChannelTypeEnum.SLACK.value:
            body["text"] = (
                f"IAM alert: {payload.get('event_type', '')} "
                f"in organization {payload.get('organization_id', '')}"
            )
        try:
            self.notifications.send(
                Notification(
                    channel=channel.type,
                    destination=channel.destination,
                    payload=body,
                )
            )
        except Exception as exc:
            logger.error(
                f"Failed to deliver alert {alert.id} to {channel.type} {channel.destination}. Error: {exc}"
            )
