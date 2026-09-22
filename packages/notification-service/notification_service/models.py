from typing import Protocol

from pydantic import BaseModel, Field


class Notification(BaseModel):
    channel: str
    destination: str = ""
    payload: dict = Field(default_factory=dict)


class NotificationPort(Protocol):
    def send(self, notification: Notification) -> None: ...
