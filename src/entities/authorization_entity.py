from typing import Optional

from pydantic import BaseModel

from entities.enum.role_enum import RoleEnum
from entities.enum.user_type_enum import UserTypeEnum


class AuthorizationRequestorEntity(BaseModel):
    role: Optional[RoleEnum] = RoleEnum.REGULAR
    organization_id: Optional[str] = None
    user_type: Optional[UserTypeEnum] = UserTypeEnum.OTHER


class AuthorizationRequestedEntity(AuthorizationRequestorEntity):
    pass
