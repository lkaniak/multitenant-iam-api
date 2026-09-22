import os
from urllib.parse import urlparse

import httpx

from notification_service.models import Notification

HTTP_BASE_URL_ENV = "NOTIFICATION_HTTP_BASE_URL"
HTTP_API_KEY_ENV = "NOTIFICATION_HTTP_API_KEY"


class NotificationDeliveryError(Exception):
    pass


class HttpNotificationAdapter:
    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    @classmethod
    def from_env(cls) -> "HttpNotificationAdapter":
        return cls(
            base_url=os.environ.get(HTTP_BASE_URL_ENV, ""),
            api_key=os.environ.get(HTTP_API_KEY_ENV, ""),
        )

    def send(self, notification: Notification) -> None:
        if _is_absolute_http_url(notification.destination):
            url = notification.destination
            body = notification.payload
        else:
            if not self.base_url:
                raise NotificationDeliveryError(
                    f"{HTTP_BASE_URL_ENV} is required when destination is not an absolute URL"
                )
            url = f"{self.base_url}/notifications"
            body = notification.model_dump()
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        try:
            with httpx.Client(timeout=5.0, headers=headers) as client:
                response = client.post(url, json=body)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise NotificationDeliveryError(str(exc)) from exc


def _is_absolute_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
