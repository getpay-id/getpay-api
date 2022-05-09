import hashlib
from enum import Enum

from fastapi import Form, HTTPException, status
from pydantic import BaseModel

from app import settings
from app.core import transaction


class IPaymuStatus(str, Enum):
    berhasil = "berhasil"
    pending = "pending"


class IPaymuFormCallback(BaseModel):
    trx_id: str
    status: IPaymuStatus


async def ipaymu(trx_id: str = Form(...), status: IPaymuStatus = Form(...)):
    """
    Endpoint to handle payments from ipaymu
    """
    if status == IPaymuStatus.berhasil:
        await transaction.paid(trx_id=trx_id, message="IPaymu")

    return {"detail": "ok"}


async def duitku(
    merchantCode: str = Form(...),
    amount: int = Form(...),
    merchantOrderId: str = Form(...),
    productDetail: str = Form(None),
    additionalParam: str = Form(None),
    paymentCode: str = Form(...),
    resultCode: str = Form(...),
    merchantUserId: str = Form(...),
    reference: str = Form(...),
    signature: str = Form(...),
    spUserHash: str = Form(None),
):
    """
    Endpoint to handle payments from duitku
    """

    secret_key = hashlib.md5(
        f"{merchantCode}{amount}{merchantOrderId}{settings.DUITKU_API_KEY}".encode()
    ).hexdigest()
    if signature != secret_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )

    if resultCode == "00":
        await transaction.paid(trx_id=merchantOrderId, message="Duitku")

    return {"detail": "ok"}
