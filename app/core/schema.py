from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Schema(BaseModel):
    id: str
    date_created: datetime
    date_updated: Optional[datetime]
