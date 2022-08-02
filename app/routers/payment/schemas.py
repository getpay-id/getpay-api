from typing import List, Optional

from pydantic import BaseModel, StrictFloat, StrictInt

from app.core.fields import Image


class PublicPaymentChannelOut(BaseModel):
    name: str
    code: str
    fee: Optional[StrictInt]
    fee_percent: Optional[StrictFloat]
    min_amount: Optional[int]
    img: Optional[Image]


class PublicPaymentMethodOut(BaseModel):
    name: str
    code: str
    channels: List[PublicPaymentChannelOut]
