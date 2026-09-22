from enum import Enum


class RoleEnum(Enum):
    ADMIN = "admin"
    REGULAR = "regular"
    OWNER = "owner"

    @classmethod
    def from_str(cls, role: str):
        try:
            return RoleEnum(role)
        except KeyError:
            return RoleEnum.REGULAR
