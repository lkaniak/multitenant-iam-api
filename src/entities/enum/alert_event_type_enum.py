from enum import Enum


class AlertEventTypeEnum(Enum):
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"
    LOGIN_FAILED = "login_failed"
    PERMISSION_DENIED = "permission_denied"

    @classmethod
    def from_str(cls, event_type: str):
        try:
            return AlertEventTypeEnum(event_type)
        except ValueError:
            return None
