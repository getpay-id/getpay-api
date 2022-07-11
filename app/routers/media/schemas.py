from pydantic import BaseModel

from app.core.schema import Schema


class MediaSchema(Schema):
    file: str


class SuccessDeleteMedia(BaseModel):
    success: bool
