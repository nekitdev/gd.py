from typing import Any, TypeVar

from typing_aliases import StringDict

from gd.string_utils import snake_to_camel

__all__ = ("NamedDict", "CamelDict")

T = TypeVar("T")

D = TypeVar("D", bound="AnyNamedDict")


class NamedDict(StringDict[T]):
    def copy(self: D) -> D:
        return type(self)(self)

    def __getattr__(self, name: str) -> T:
        try:
            return self[name]

        except KeyError as error:
            raise AttributeError(name) from error


AnyNamedDict = NamedDict[Any]


class CamelDict(NamedDict[T]):
    def __getattr__(self, name: str) -> T:
        return super().__getattr__(snake_to_camel(name))


AnyCamelDict = CamelDict[Any]
