import os
from typing import Tuple

from bson import ObjectId
from fastapi import File, HTTPException, Query, Request, UploadFile, status
from filetype import is_image
from pymongo.collection import ReturnDocument
from pymongo.results import DeleteResult, InsertOneResult

from app import collections, settings
from app.core import timezone, utils
from app.core.constants import BASE_PATH, STATIC_PAYMENT_IMAGES_PATH
from app.core.enums import SortBy
from app.core.fields import ObjectID
from app.core.pagination import paginate


async def _validate_file(request: Request, file: UploadFile) -> Tuple[str, bytes]:
    if "content-length" not in request.headers:
        raise HTTPException(status.HTTP_411_LENGTH_REQUIRED)

    cl = int(request.headers["content-length"])
    if cl > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    buffer = await file.read()
    if not is_image(buffer):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    outfile = str(STATIC_PAYMENT_IMAGES_PATH / file.filename)
    if os.path.isfile(outfile):
        filename, ext = os.path.splitext(outfile)
        filename += utils.generate_random_string(3)
        outfile = f"{filename}{ext}"

    outfile = outfile.replace(str(BASE_PATH), "").lstrip("/")
    return outfile, buffer


async def upload(request: Request, file: UploadFile = File(...)) -> str:
    """
    Mengunggah file.
    """
    outfile, buffer = await _validate_file(request, file)
    with open(outfile, "wb") as fp:
        fp.write(buffer)

    data = {"file": "/" + outfile, "date_created": timezone.now(), "date_updated": None}
    obj: InsertOneResult = await collections.media.insert_one(data)
    data["id"] = str(obj.inserted_id)
    return data


async def delete(request: Request, id: ObjectID):
    """
    Menghapus objek media dengan ID.
    """
    obj_id = {"_id": ObjectId(id)}
    data: dict = await collections.media.find_one(obj_id)
    if not data:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    fileloc = data["file"].lstrip("/")
    if os.path.isfile(fileloc):
        os.remove(fileloc)

    result: DeleteResult = await collections.media.delete_one(obj_id)
    success = result.deleted_count > 0
    return {"success": success}


async def update(request: Request, id: ObjectID, file: UploadFile = File(...)):
    """
    Perbarui data objek media.
    """
    obj_id = {"_id": ObjectId(id)}
    data: dict = await collections.media.find_one(obj_id)
    if not data:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    outfile: str = data["file"]
    _, buffer = await _validate_file(request, file)
    with open(outfile.lstrip("/"), "wb") as fp:
        fp.write(buffer)

    obj_id = {"_id": ObjectId(id)}
    data: dict = await collections.media.find_one_and_update(
        obj_id,
        {"$set": {"date_updated": timezone.now()}},
        return_document=ReturnDocument.AFTER,
    )
    return utils.serialize_data(data)


async def get_all(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: SortBy = Query(
        SortBy.desc, description="Sort by ASCENDING (1) or DESCENDING (-1)"
    ),
):
    """
    Mendapatkan semua objek media.
    """
    return await paginate(
        collections.media,
        page,
        size,
        sort_field=("date_created", sort_by),
    )


async def get_one(request: Request, id: ObjectID):
    """
    Mendapatkan rincian objek media.
    """
    obj_id = {"_id": ObjectId(id)}
    data: dict = await collections.media.find_one(obj_id)
    if not data:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return utils.serialize_data(data)
