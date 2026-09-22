from pydantic import BaseModel, Field


class TokenBase(BaseModel):

    access_token: bytes = Field(...)
    expiration: int = Field(15 * 60 * 60 * 24 * 7)
