from datetime import datetime
from typing import Optional

from app.core.enums import ExpirationType
from app.core.schema import Schema


class APIKeyDetail(Schema):
    name: str
    description: str
    expiration_time: int
    expiration_type: ExpirationType
    secret_key: str
    token: str
    expires_on: Optional[datetime]


class PublicAPIKey(Schema):
    name: str
    description: str
    expiration_time: int
    expiration_type: ExpirationType
    expires_on: Optional[datetime]
