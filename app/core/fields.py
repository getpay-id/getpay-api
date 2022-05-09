import os
from typing import Callable, Generator

from bson import ObjectId as _ObjectId
from pydantic import AnyHttpUrl, AnyUrl, BaseConfig
from pydantic.fields import ModelField


class ObjectID(str):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, oid: str) -> _ObjectId:
        if not isinstance(oid, str):
            raise TypeError("ObjectID must be a string")
        if not _ObjectId.is_valid(oid):
            raise ValueError("ID is not valid")
        return oid


class Image(AnyHttpUrl):
    @classmethod
    def validate(
        cls, value: str, field: "ModelField", config: "BaseConfig"
    ) -> "AnyUrl":
        super().validate(value, field, config)
        _, ext = os.path.splitext(os.path.basename(value))
        if ext not in [".jpg", ".jpeg", ".png", ".svg"]:
            raise ValueError("Image required")

        return value
