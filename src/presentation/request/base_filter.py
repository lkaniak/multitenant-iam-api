from typing import Optional

from bson import ObjectId
from pydantic import Field, field_validator

from entities.exceptions.invalid_id_exception import InvalidIdException
from entities.pydantic_entity import BaseModelExtended


class BaseFilter(BaseModelExtended):
    id: Optional[str] = Field(None, description="Entity id")
    ids: Optional[list[str]] = Field(None, description="Entity ids")

    @field_validator("id")
    def check_id(cls, id):
        if id and not ObjectId.is_valid(id):
            raise InvalidIdException()
        return id

    @field_validator("ids")
    def check_ids(cls, ids):
        for id in ids:
            if not ObjectId.is_valid(id):
                raise InvalidIdException()
        return ids
