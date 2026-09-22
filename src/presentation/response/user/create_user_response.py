from pydantic import Field

from entities.enum.role_enum import RoleEnum
from entities.pydantic_entity import BaseModelExtended
from entities.user_entity import UserContactInfoEntity


class CreateUserResponse(BaseModelExtended):
    id: str = Field("", description="User id")
    username: str = Field("", description="User username")
    role: str = Field(RoleEnum.REGULAR.value, description="User role")
    contact_info: UserContactInfoEntity = Field(
        default_factory=UserContactInfoEntity, description="user contact info"
    )
