from abc import abstractmethod
from builtins import isinstance as is_instance
from functools import partial
from json import dump as standard_dump
from json import dumps as standard_dumps
from json import load as standard_load
from json import loads as standard_loads
from typing import Any, Type, TypeVar

from typing_extensions import Protocol, TypeGuard, runtime_checkable

from gd.text_utils import snake_to_camel
from gd.typing import JSONType, StringDict, is_instance, is_iterable, is_mapping

__all__ = (
    "FromJSON",
    "ToJSON",
    "JSON",
    "is_from_json",
    "is_to_json",
    "NamedDict",
    "CamelDict",
    "default",
    "dump",
    "dumps",
    "load",
    "loads",
)

A = TypeVar("A")

J = TypeVar("J", bound=JSONType)

JP = TypeVar("JP", bound=JSONType, covariant=True)
JM = TypeVar("JM", bound=JSONType, contravariant=True)

F = TypeVar("F", bound="FromJSONType")


@runtime_checkable
class FromJSON(Protocol[JM]):
    @classmethod
    @abstractmethod
    def from_json(cls: Type[F], data: JM) -> F:
        ...


FromJSONType = FromJSON[JSONType]


def is_from_json(some: Any) -> TypeGuard[FromJSONType]:
    return is_instance(some, FromJSONType)


@runtime_checkable
class ToJSON(Protocol[JP]):
    @abstractmethod
    def to_json(self) -> JP:
        ...


ToJSONType = ToJSON[JSONType]


def is_to_json(some: Any) -> TypeGuard[ToJSONType]:
    return is_instance(some, ToJSONType)


@runtime_checkable
class JSON(FromJSON[J], ToJSON[J], Protocol[J]):
    pass


D = TypeVar("D", bound="AnyNamedDict")


class NamedDict(StringDict[A]):
    def copy(self: D) -> D:
        return type(self)(self)

    def __getattr__(self, name: str) -> A:
        try:
            return self[name]

        except KeyError as error:
            raise AttributeError(name) from error


AnyNamedDict = NamedDict[Any]


class CamelDict(NamedDict[A]):
    def __getattr__(self, name: str) -> A:
        return super().__getattr__(snake_to_camel(name))


AnyCamelDict = CamelDict[Any]


NOT_JSON_SERIALIZABLE = "{} instance is not JSON-serializable"


def default(some: Any) -> JSONType:
    if is_to_json(some):
        return some.to_json()

    if is_mapping(some):
        return dict(some)

    if is_iterable(some):
        return list(some)

    raise TypeError(NOT_JSON_SERIALIZABLE)


dump = partial(standard_dump, default=default)
dumps = partial(standard_dumps, default=default)
load = partial(standard_load, object_hook=NamedDict)
loads = partial(standard_loads, object_hook=NamedDict)
