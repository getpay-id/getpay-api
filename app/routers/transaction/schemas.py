from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, StrictFloat, StrictInt

from app.core.enums import TransactionStatus
from app.core.schema import Schema


class TransactionPaymentChannelOut(BaseModel):
    name: str
    fee: StrictInt
    fee_percent: StrictFloat


class TransactionOut(Schema):
    name: str
    email: EmailStr
    phone_number: str
    amount: int
    payment_method: str
    payment_channel: TransactionPaymentChannelOut
    payment_number: Any
    expiration_date: datetime
    status: TransactionStatus
    trx_id: str


class UpdateTransactionOut(BaseModel):
    success: bool
    data: TransactionOut
