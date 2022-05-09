import orjson
from fastapi import HTTPException, Request, status

from app.core import transaction


async def load_body(request: Request) -> dict:
    raw_body = await request.body()
    data = orjson.loads(raw_body)
    if not isinstance(data, dict):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
    return data


async def virtual_account(request: Request):
    """
    Endpoint to handle payments (Virtual Account) from xendit
    """

    request_body = await load_body(request)
    trx_id = request_body.get("id")
    if not trx_id:
        return {"detail": "ok"}

    if "callback_virtual_account_id" in request_body:
        msg_prefix = "Xendit(virtual account)"
        await transaction.paid(trx_id=trx_id, message=msg_prefix)

    return {"detail": "ok"}


async def ewallet(request: Request):
    """
    Endpoint to handle payments (E-Wallet) from xendit
    """

    request_body = await load_body(request)
    info: dict = request_body.get("data", {})
    trx_id = info.get("id")
    if not trx_id:
        return {"detail": "ok"}

    if request_body.get("status") == "SUCCEEDED":
        msg_prefix = "Xendit(ewallet)"
        await transaction.paid(trx_id=trx_id, message=msg_prefix)

    return {"detail": "ok"}


async def convenience_store(request: Request):
    """
    Endpoint to handle payments (Convenience Store) from xendit
    """

    request_body = await load_body(request)
    trx_id = request_body.get("id")
    if not trx_id:
        return {"detail": "ok"}

    status = request_body.get("status")
    if status == "COMPLETED":
        msg_prefix = "Xendit(cstore)"
        await transaction.paid(trx_id=trx_id, message=msg_prefix)

    return {"detail": "ok"}


async def qris(request: Request):
    """
    Endpoint to handle payments (QRCode) from xendit
    """

    request_body = await load_body(request)
    trx_id = request_body.get("id")
    if not trx_id:
        return {"detail": "ok"}

    status = request_body.get("status")
    if status == "COMPLETED":
        msg_prefix = "Xendit(qrcode)"
        await transaction.paid(trx_id=trx_id, message=msg_prefix)

    return {"detail": "ok"}
