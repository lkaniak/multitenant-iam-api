from bson import ObjectId
from fastapi import Path

from entities.exceptions.invalid_id_exception import InvalidIdException


def verify_object_id(id: str = Path(...)) -> str:

    if not ObjectId.is_valid(id):
        raise InvalidIdException()

    return id
