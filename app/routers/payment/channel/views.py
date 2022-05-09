from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, Path, Query, status
from pydantic import BaseModel, StrictFloat, StrictInt
from pymongo import ReturnDocument

from app import collections
from app.core import timezone
from app.core.enums import PaymentStatus, SortBy
from app.core.fields import Image, ObjectID
from app.core.pagination import paginate
from app.core.utils import serialize_data


class PaymentChannelIn(BaseModel):
    fee: Optional[StrictInt]
    fee_percent: Optional[StrictFloat]
    status: PaymentStatus
    name: str
    img: Optional[Image]


async def get_all(
    id: ObjectID = Query(..., description="Payment Method ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: SortBy = Query(
        SortBy.desc, description="Sort by ASCENDING (1) or DESCENDING (-1)"
    ),
):
    """
    Mendapatkan semua payment channel di payment methods.
    """
    return await paginate(
        collections.payment_channel,
        page,
        size,
        query_filter={"pm_id": id},
        sort_field=("date_updated", sort_by),
    )


async def get_one(
    id: ObjectID = Path(..., description="Payment Channel ID"),
):
    """
    Mendapatkan rincian payment channel.
    """
    obj = await collections.payment_channel.find_one({"_id": ObjectId(id)})
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    data = serialize_data(obj)
    return data


async def update(
    body: PaymentChannelIn,
    id: ObjectID = Path(..., description="Payment Channel ID"),
):
    """
    Memperbarui payment channel.

    Parameters:

    * `fee`: Biaya transaksi tetap

    * `fee_percent`: Biaya transaksi dalam persen

    * `status`: Status payment channel (0 = inactive, 1 = active)

    * `name`: Nama payment channel

    * `img`: URL Gambar untuk payment channel
    """

    payload = body.dict()
    payload["date_updated"] = timezone.now()
    obj = await collections.payment_channel.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": payload},
        return_document=ReturnDocument.AFTER,
    )
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    data = serialize_data(obj)
    return data
