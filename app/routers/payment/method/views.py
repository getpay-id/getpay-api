from bson import ObjectId
from fastapi import HTTPException, Path, Query, status
from pydantic import BaseModel
from pymongo import ReturnDocument

from app import collections
from app.core import timezone
from app.core.enums import PaymentStatus, SortBy
from app.core.fields import ObjectID
from app.core.pagination import paginate
from app.core.utils import serialize_data


class BodyPaymentMethod(BaseModel):
    status: PaymentStatus


async def get_all(
    pg_id: ObjectID = Query(..., description="Payment gateway ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: SortBy = Query(
        SortBy.desc, description="Sort by ASCENDING (1) or DESCENDING (-1)"
    ),
):
    """
    Mendapatkan semua payment methods.
    """

    return await paginate(
        collections.payment_method,
        page,
        size,
        query_filter={"pg_id": pg_id},
        sort_field=("date_created", sort_by),
    )


async def get_one(
    id: ObjectID = Path(..., description="Payment method ID"),
):
    """
    Mendapatkan rincian payment method.
    """

    pm = await collections.payment_method.find_one({"_id": ObjectId(id)})
    if not pm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    data = serialize_data(pm)
    return data


async def update(
    body: BodyPaymentMethod, id: ObjectID = Path(..., description="Payment method ID")
):
    """
    Perbarui status payment method.

    Parameters:

    * `status`: Status payment method. (0 = inactive, 1 = active)
    """

    pm = await collections.payment_method.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {"status": body.status, "date_updated": timezone.now()}},
        return_document=ReturnDocument.AFTER,
    )
    if not pm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found"
        )

    data = serialize_data(pm)
    return data
