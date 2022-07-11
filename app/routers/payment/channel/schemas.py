from typing import Optional

from pydantic import StrictFloat, StrictInt

from app.core.enums import PaymentStatus
from app.core.fields import Image
from app.core.schema import Schema


class PaymentChannel(Schema):
    pm_id: str
    name: str
    unique_code: str
    fee: Optional[StrictInt]
    fee_percent: Optional[StrictFloat]
    status: PaymentStatus
    min_amount: Optional[int]
    img: Optional[Image]
