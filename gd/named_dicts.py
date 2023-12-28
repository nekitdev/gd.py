from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from typing_aliases import StringDict

from gd.string_utils import snake_to_camel

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("NamedDict", "CamelDict")

T = TypeVar("T")


class NamedDict(StringDict[T]):
    def copy(self) -> Self:
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
