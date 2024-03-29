import asyncio
import functools
import random
import string
import time
import typing as t
from urllib.parse import quote

from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from app import settings

T = t.TypeVar("T")


def generate_random_string(
    length: int = 10, chars: str = string.ascii_letters + string.digits
) -> str:
    """
    Generate a random string of fixed length
    """

    return "".join(random.choice(chars) for i in range(length))


custom_encoder = {ObjectId: lambda obj: str(obj)}


def _rename_object_id(data: dict):
    data = data.copy()
    data["id"] = data.pop("_id")
    return data


def serialize_data(data: T) -> T:
    """
    Serialize data from mongo
    """

    if data is None:
        return

    data = jsonable_encoder(data, custom_encoder=custom_encoder)
    if isinstance(data, dict):
        return _rename_object_id(data)
    else:
        rv = []
        for d in data:
            rv.append(_rename_object_id(d))
        return rv


def timer(func: T) -> T:
    if asyncio.iscoroutinefunction(func):

        async def wrapper(*args, **kwds):
            start_time = time.perf_counter()
            rv = await func(*args, **kwds)
            end_time = time.perf_counter() - start_time
            print(f"{func.__name__} took {end_time} seconds")
            return rv

    else:

        def wrapper(*args, **kwds):
            start_time = time.perf_counter()
            rv = func(*args, **kwds)
            end_time = time.perf_counter() - start_time
            print(f"{func.__name__} took {end_time} seconds")
            return rv

    return functools.wraps(func)(wrapper)


def get_redis_url(
    *,
    host: str = None,
    port: int = 6379,
    username: str = None,
    password: str = None,
    db: int = 0,
) -> str:
    host = host or settings.REDIS_HOST
    port = port or settings.REDIS_PORT
    username = username or settings.REDIS_USERNAME
    password = password or settings.REDIS_PASSWORD
    db = db or settings.REDIS_DATABASE
    redis_auth = ""
    if username:
        redis_auth += f"{quote(username, safe='')}:"

    if password:
        redis_auth = redis_auth.rstrip(":") + ":" + quote(password, safe="") + "@"

    url = f"redis://{redis_auth}{host}:{port}/{db}"
    return url
