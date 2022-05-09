from typing import Generic, List, TypeVar

from pydantic import Extra
from pydantic.generics import GenericModel

from app.core.schema import Schema


class User(Schema):
    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True

    username: str
    password: str

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.username})"


GenericResultsType = TypeVar("GenericResultsType")


class Page(GenericModel, Generic[GenericResultsType]):
    total: int
    data: List[GenericResultsType]
