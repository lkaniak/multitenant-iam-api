from enum import Enum


class UserTypeEnum(Enum):
    SYSTEM_ADMIN = "system_admin"
    OTHER = "other"

    @classmethod
    def from_str(cls, type: str):
        try:
            return UserTypeEnum(type)
        except KeyError:
            return UserTypeEnum.OTHER
