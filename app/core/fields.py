import os
from typing import Callable, Generator

from bson import ObjectId as _ObjectId
from pydantic import AnyUrl, BaseConfig
from pydantic.fields import ModelField


class ObjectID(str):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, oid: str) -> str:
        if not isinstance(oid, str):
            raise TypeError("ID must be a string")
        if not _ObjectId.is_valid(oid):
            raise ValueError("Invalid ID")
        return oid


class Image(str):
    @classmethod
    def validate(
        cls, value: str, field: "ModelField", config: "BaseConfig"
    ) -> "AnyUrl":
        _, ext = os.path.splitext(os.path.basename(value))
        if ext not in [".jpg", ".jpeg", ".png", ".svg"]:
            raise ValueError("Image required")

        return value
