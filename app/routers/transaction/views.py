from datetime import timedelta
from typing import Optional

from bson import ObjectId
from faker import Faker
from fastapi import HTTPException, Query, Request, status
from fastapi.responses import ORJSONResponse
from popol.cache.decorators import cached
from popol.jobs.saq.globals import saq_queue
from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field, validator
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult

from app import collections, settings
from app.core import timezone
from app.core.enums import (
    PaymentGateway,
    PaymentMethod,
    PaymentStatus,
    SortBy,
    TransactionStatus,
)
from app.core.fields import ObjectID
from app.core.pagination import paginate
from app.core.thirdparty import duitku, ipaymu, xendit
from app.core.utils import generate_random_string, serialize_data
from app.extensions.ratelimit import limiter

faker = Faker()


class TransactionIn(BaseModel):
    name: str
    phone_number: str = Field(max_length=15)
    email: Optional[EmailStr]
    amount: int
    payment_method: str
    payment_channel: str
    ewallet_success_redirect_url: Optional[AnyHttpUrl]

    @validator("name")
    def validate_name(cls, v: str, values: dict, **kwargs):
        if not all(c.isalnum() or c.isspace() for c in v):
            raise ValueError("name must be alphanumeric")
        return v

    @validator("phone_number")
    def validate_phone_number(cls, v: str, values: dict, **kwargs):
        if not v.isdigit():
            raise ValueError("phone_number must be a number")

        length = len(v)
        if length < 9 or length > 15:
            raise ValueError("phone_number must be greater than 9 and less than 15")

        if not v.startswith("08"):
            raise ValueError("phone_number must start with 08")

        return v


class UpdateTransactionIn(BaseModel):
    status: TransactionStatus


async def create(request: Request, body: TransactionIn):
    """
    Buat transaksi baru

    Parameter:

    * `name`: Nama pembeli

    * `phone_number`: Nomor telepon pembeli

    * `email`: Email pembeli (optional)

    * `amount`: Jumlah yang dibayar

    * `payment_method`: Kode metode pembayaran (contoh: `va`, `cstore`, dll)

    * `payment_channel`: Kode channel pembayaran (contoh: `xQkS3l`, `9iLS23`, dll) (Catatan: ini adalah karakter acak dengan panjang 6 karakter)

    * `ewallet_success_redirect_url`: URL untuk di redirect jika pembayaran berhasil (optional) (required untuk metode pembayaran *ewallet*)
    """

    pg_name: str = None
    pc_obj: dict = None
    for pg in PaymentGateway:
        pg_obj: dict = await collections.payment_gateway.find_one(
            {"name": pg.value, "status": PaymentStatus.active}
        )
        if pg_obj:
            pg_name = pg.value
            async for pm_obj in collections.payment_method.find(
                {
                    "pg_id": str(pg_obj["_id"]),
                    "code": body.payment_method,
                    "status": PaymentStatus.active,
                }
            ):
                pm_id: str = str(pm_obj["_id"])
                pc_obj = await collections.payment_channel.find_one(
                    {
                        "pm_id": pm_id,
                        "unique_code": body.payment_channel,
                        "status": PaymentStatus.active,
                    }
                )
                if pc_obj:
                    break

            if pc_obj:
                break

    if not pc_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Payment not found"
        )

    payment_code: str = pc_obj["code"]
    exp_trx = timedelta(hours=1)
    expiration_date = timezone.now() + exp_trx
    email = body.email or "gp-" + faker.email()
    amount = body.amount
    amount += pc_obj["fee"] or 0
    amount += round(amount * (pc_obj["fee_percent"] or 0) // 100)
    min_amount = pc_obj.get("min_amount") or 0
    if amount < min_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than or equal to {}".format(min_amount),
        )

    payload = {
        "name": body.name,
        "phone_number": body.phone_number,
        "email": email,
        "amount": amount,
        "payment_method": body.payment_method,
        "payment_channel": serialize_data(pc_obj),
        "expiration_date": expiration_date,
        "status": TransactionStatus.pending,
        "date_created": timezone.now(),
        "date_updated": None,
        "paid_date": None,
    }
    if pg_name == PaymentGateway.ipaymu:
        api_key = settings.IPAYMU_API_KEY
        url = settings.IPAYMU_URL
        callback_url = settings.IPAYMU_CALLBACK_URL
        va_account = settings.IPAYMU_VIRTUAL_ACCOUNT
        resp = ipaymu.direct_payment(
            url=url,
            va_account=va_account,
            api_key=api_key,
            name=body.name,
            phone=body.phone_number,
            email=email,
            amount=amount,
            notifyUrl=callback_url,
            expired=1,
            expiredType="hours",
            paymentMethod=body.payment_method,
            paymentChannel=payment_code,
        )
        if resp["Status"] != 200:
            detail = "IPaymu: " + resp.get("Message", "Unknown error")
            data = resp.get("Error")
            return ORJSONResponse(
                {"detail": detail, "data": data},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        i_data = resp["Data"]
        payload["trx_id"] = str(
            i_data["TransactionId"]
        )  # Make sure the type of `trx_id` is String
        payload["payment_number"] = i_data["PaymentNo"]
        payload["amount"] = i_data["Total"]

    elif pg_name == PaymentGateway.xendit:
        api_key = settings.XENDIT_API_KEY
        ext_id = generate_random_string()
        payment_code = payment_code.upper()
        expiration_date = expiration_date.isoformat()
        if body.payment_method == PaymentMethod.va:
            success, resp = xendit.create_virtual_account_payment(
                api_key=api_key,
                external_id=ext_id,
                bank_code=payment_code,
                name=body.name,
                expected_amount=amount,
                expiration_date=expiration_date,
            )
            if not success:
                if "That bank code is not currently supported" in resp.get(
                    "detail", ""
                ):
                    await collections.payment_channel.find_one_and_update(
                        {"_id": pc_obj["_id"]},
                        {"$set": {"status": PaymentStatus.inactive}},
                    )
                return ORJSONResponse(resp, status_code=status.HTTP_400_BAD_REQUEST)

            payload["trx_id"] = resp.id
            payload["payment_number"] = resp.account_number
            payload["amount"] = resp.expected_amount

        elif body.payment_method == PaymentMethod.qris:
            callback_url = settings.XENDIT_QRCODE_CALLBACK_URL
            success, resp = xendit.create_qris_payment(
                api_key=api_key,
                external_id=ext_id,
                callback_url=callback_url,
                amount=amount,
            )
            if not success:
                return ORJSONResponse(resp, status_code=status.HTTP_400_BAD_REQUEST)

            payload["trx_id"] = resp.id
            payload["payment_number"] = resp.qr_string
            payload["amount"] = resp.amount

        elif body.payment_method == PaymentMethod.cstore:
            success, resp = xendit.create_retail_outlet_payment(
                api_key=api_key,
                external_id=ext_id,
                retail_outlet_name=payment_code,
                name=body.name,
                expected_amount=amount,
                expiration_date=expiration_date,
            )
            if not success:
                return ORJSONResponse(resp, status_code=status.HTTP_400_BAD_REQUEST)

            payload["trx_id"] = resp.id
            payload["payment_number"] = resp.payment_code
            payload["amount"] = resp.expected_amount

        elif body.payment_method == PaymentMethod.ewallet:
            if not body.ewallet_success_redirect_url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ewallet_success_redirect_url is required",
                )

            channel_props = {"success_redirect_url": body.ewallet_success_redirect_url}
            if payment_code == "ID_OVO":
                channel_props["mobile_number"] = "+62" + body.phone_number[1:]

            success, resp = xendit.create_ewallet_payment(
                api_key=api_key,
                external_id=ext_id,
                amount=amount,
                channel_code=payment_code,
                channel_properties=channel_props,
            )
            if not success:
                return ORJSONResponse(resp, status_code=status.HTTP_400_BAD_REQUEST)

            payload["trx_id"] = resp.id
            payload["payment_number"] = resp.actions
            payload["amount"] = resp.charge_amount

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment method"
            )

    elif pg_name == PaymentGateway.duitku:
        url = settings.DUITKU_URL
        api_key = settings.DUITKU_API_KEY
        merchant_code = settings.DUITKU_MERCHANT_CODE
        trx_id, resp = duitku.request_transaction(
            url,
            api_key,
            merchant_code,
            name=body.name,
            email=email,
            phone_number=body.phone_number,
            amount=amount,
            paymentMethod=payment_code,
            expiryPeriod=60,  # 1 hour
        )
        resp_content: dict = resp.json()
        if resp.status_code == 200:
            payload["trx_id"] = trx_id
            payload["amount"] = resp_content.get(
                "amount", amount
            )  # untuk metode pembayaran BRIVA tidak ada field amount.
            if body.payment_method in (PaymentMethod.va, PaymentMethod.cstore):
                payload["payment_number"] = resp_content["vaNumber"]
            elif body.payment_method == PaymentMethod.ewallet:
                checkout_url = resp_content["paymentUrl"]
                payload["payment_number"] = {
                    "desktop_web_checkout_url": checkout_url,
                    "mobile_web_checkout_url": checkout_url,
                    "mobile_deeplink_checkout_url": None,
                    "qr_checkout_string": None,
                }
            elif body.payment_method == PaymentMethod.qris:
                payload["payment_number"] = resp_content["qrString"]
        else:
            detail = "Duitku: " + resp_content.get("Message", "Unknown error")
            if "payment channel not available" in detail.lower():
                await collections.payment_channel.find_one_and_update(
                    {"_id": pc_obj["_id"]},
                    {
                        "$set": {
                            "status": PaymentStatus.inactive,
                            "date_updated": timezone.now(),
                        }
                    },
                )

            return ORJSONResponse(
                {"detail": detail},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Invalid payment gateway",
        )

    result: InsertOneResult = await collections.transactions.insert_one(payload)
    obj = await collections.transactions.find_one({"_id": result.inserted_id})
    data = serialize_data(obj)
    scheduled = int((timezone.now() + exp_trx).timestamp())
    await saq_queue.enqueue(
        "update_transaction_status", trx_id=str(result.inserted_id), scheduled=scheduled
    )
    return data


if settings.DEMO:
    create = limiter.limit("1/10 minute")(create)


async def get_one(id: ObjectID):
    """
    Mendapatkan rincian transaksi
    """
    obj = await collections.transactions.find_one({"_id": ObjectId(id)})
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    data = serialize_data(obj)
    return data


@cached()
async def get_all(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: SortBy = Query(
        SortBy.desc, description="Sort by ASCENDING (1) or DESCENDING (-1)"
    ),
):
    """
    Mendapatkan semua transaksi
    """

    return await paginate(
        collections.transactions, page, size, sort_field=("date_created", sort_by)
    )


async def update(id: ObjectID, body: UpdateTransactionIn):
    """
    Perbarui status transaksi.

    Parameters:

    * `status`: Status transaksi. (0 = pending, 1 = success, 2 = expired)
    """

    obj = await collections.transactions.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {"status": body.status, "date_updated": timezone.now()}},
        return_document=ReturnDocument.AFTER,
    )
    if obj:
        success = True
    else:
        success = False
    data = serialize_data(obj)
    return {"success": success, "data": data}
