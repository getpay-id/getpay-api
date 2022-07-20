from bson import ObjectId, Regex
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, Query, Request, status
from pydantic import BaseModel, validator
from pymongo import ReturnDocument
from pymongo.results import DeleteResult, InsertOneResult

from app import collections
from app.core import fernet, timezone
from app.core.constants import ALPHA_NUMERIC_RE
from app.core.enums import ExpirationType, SortBy
from app.core.fields import ObjectID
from app.core.pagination import paginate
from app.core.utils import serialize_data


class APIKeyIn(BaseModel):
    name: str
    description: str
    expiration_time: int
    expiration_type: ExpirationType

    @validator("expiration_type")
    def validate_expiration_type(cls, v, values: dict, **kwargs):
        if v != ExpirationType.unlimited and values["expiration_time"] <= 0:
            raise ValueError("expiration_time must be greater than 0")
        elif v == ExpirationType.unlimited and values["expiration_time"] > 0:
            raise ValueError("expiration_time must be 0")
        return v


class UpdateAPIKey(BaseModel):
    name: str
    description: str


async def create(request: Request, body: APIKeyIn):
    """
    Buat API Key baru

    Parameters:

    * `name`: Nama API Key

    * `description`: Deskripsi API Key

    * `expiration_time`: Lama aktif API Key (integer)

    * `expiration_type`: Tipe aktif API Key (unlimited, minutes, hours, months, years)
    """

    payload = body.dict()
    expires_on = None
    user_id = request.state.user.id
    if body.expiration_type != ExpirationType.unlimited:
        td_params = {body.expiration_type.value: body.expiration_time}
        td_obj = relativedelta(**td_params)
        expires_on = timezone.now() + td_obj
        secret_key, token = fernet.create(user_id, td_obj)
    else:
        secret_key, token = fernet.create(user_id)

    payload["secret_key"] = secret_key
    payload["api_key"] = token
    payload["expires_on"] = expires_on
    payload["date_created"] = timezone.now()
    payload["date_updated"] = None
    result: InsertOneResult = await collections.api_keys.insert_one(payload)
    obj_id = result.inserted_id
    obj = await collections.api_keys.find_one({"_id": obj_id})
    data = serialize_data(obj)
    return data


async def get_one(id: ObjectID):
    """
    Mendapatkan rincian API Key
    """
    obj = await collections.api_keys.find_one({"_id": ObjectId(id)})
    data = serialize_data(obj)
    return data


async def get_all(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: SortBy = Query(
        SortBy.desc, description="Sort by ASCENDING (1) or DESCENDING (-1)"
    ),
    q: str = Query(None, description="Search query"),
):
    """
    Mendapatkan daftar API Key.

    Parameters:

    * `q`: Pencarian berdasarkan nama dan deskripsi API Key

    """

    qs = {}
    if q and ALPHA_NUMERIC_RE.match(q):
        qs["name"] = Regex(q, "i")
        qs["description"] = Regex(q, "i")

    return await paginate(
        collections.api_keys,
        page,
        size,
        query_filter=qs,
        sort_field=("date_created", sort_by),
    )


async def update(id: ObjectID, body: UpdateAPIKey):
    """
    Perbarui API Key

    Parameters:

    * `name`: Nama API Key

    * `description`: Deskripsi API Key

    """

    payload = body.dict()
    payload["date_updated"] = timezone.now()
    obj = await collections.api_keys.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": payload}, return_document=ReturnDocument.AFTER
    )
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "API Key not found")

    data = serialize_data(obj)
    return data


async def delete(id: ObjectID):
    """
    Hapus API Key
    """

    obj: DeleteResult = await collections.api_keys.delete_one({"_id": ObjectId(id)})
    success = True if obj.deleted_count == 1 else False
    return {"success": success}
