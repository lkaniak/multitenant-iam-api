from enum import Enum


class AlertChannelTypeEnum(Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"

    @classmethod
    def from_str(cls, channel_type: str):
        try:
            return AlertChannelTypeEnum(channel_type)
        except ValueError:
            return None
