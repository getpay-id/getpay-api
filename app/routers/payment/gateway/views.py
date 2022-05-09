from bson import ObjectId
from fastapi import HTTPException, Query, status
from pydantic import BaseModel
from pymongo import ReturnDocument

from app import collections
from app.core import timezone
from app.core.enums import PaymentStatus, SortBy
from app.core.fields import ObjectID
from app.core.pagination import paginate
from app.core.utils import serialize_data


class PaymentGatewayIn(BaseModel):
    status: PaymentStatus


async def get_all(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: SortBy = Query(
        SortBy.desc, description="Sort by ASCENDING (1) or DESCENDING (-1)"
    ),
):
    """
    Mendapatkan semua payment gateway.
    """

    return await paginate(
        collections.payment_gateway,
        page,
        size,
        sort_field=("date_updated", sort_by),
    )


async def update(id: ObjectID, body: PaymentGatewayIn):
    """
    Perbarui status payment gateway.

    Parameters:

    * `status`: Status payment gateway. (0 = inactive, 1 = active)
    """

    id = ObjectId(id)
    rv = await collections.payment_gateway.find_one_and_update(
        {"_id": id},
        {"$set": {"status": body.status, "date_updated": timezone.now()}},
        return_document=ReturnDocument.AFTER,
    )
    if rv:
        data = serialize_data(rv)
        return data
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not found")
