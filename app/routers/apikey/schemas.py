from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.core.enums import ExpirationType
from app.core.schema import Schema


class APIKeyDetail(Schema):
    name: str
    description: str
    expiration_time: int
    expiration_type: ExpirationType
    api_key: str
    expires_on: Optional[datetime]


class PublicAPIKey(Schema):
    name: str
    description: str
    expiration_time: int
    expiration_type: ExpirationType
    expires_on: Optional[datetime]


class SuccessDeleteAPIKey(BaseModel):
    success: bool
