from __future__ import annotations

from builtins import issubclass as is_subclass
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from attrs import define, field
from typing_extensions import Never

from gd.memory.constants import DEFAULT_EXCLUDE, DEFAULT_OFFSET
from gd.memory.data import Data
from gd.memory.pointers import PointerData
from gd.memory.special import Void
from gd.typing import StringDict, get_name, is_instance

if TYPE_CHECKING:
    from gd.memory.base import Base

__all__ = ("Field",)

T = TypeVar("T")

CAN_NOT_DELETE_FIELDS = "can not delete fields"

B = TypeVar("B", bound="Base")
F = TypeVar("F", bound="AnyField")


@define()
class Field(Generic[T]):
    data: Data[T] = field()
    offset: int = field(default=DEFAULT_OFFSET, repr=hex)
    exclude: bool = field(default=DEFAULT_EXCLUDE)

    def is_excluded(self) -> bool:
        return self.exclude

    def reset(self: F) -> F:
        return type(self)(self.data)

    @overload
    def __get__(self: F, instance: None, type: Optional[Type[B]] = ...) -> F:
        ...

    @overload
    def __get__(self, instance: B, type: Optional[Type[B]]) -> T:
        ...

    def __get__(self: F, instance: Optional[B], type: Optional[Type[B]] = None) -> Union[F, T]:
        if instance is None:
            return self

        return self.data.read(instance.state, instance.address + self.offset, instance.order)

    def __set__(self, instance: Base, value: T) -> None:
        self.data.write(instance.state, instance.address + self.offset, value, instance.order)

    def __delete__(self, instance: Base) -> Never:
        raise AttributeError(CAN_NOT_DELETE_FIELDS)


AnyField = Field[Any]

VIRTUAL_NAME = "__virtual_{}__"

virtual_name = VIRTUAL_NAME.format


def fetch_fields_iterator(base: Type[Base]) -> Iterator[Tuple[str, AnyField]]:
    types = base.mro()

    for type in reversed(types):
        if is_subclass(type, Struct) and type.VIRTUAL:
            if not any(
                is_subclass(other, Struct)
                and other is not Struct
                and other is not type
                and is_subclass(type, other)
                for other in reversed(types)
            ):
                yield (virtual_name(get_name(type)), Field(PointerData(Void()), exclude=True))

        for name, value in vars(type).items():
            if is_instance(value, Field) and not value.is_excluded():
                yield (name, value.reset())


def fetch_fields(base: Type[Base]) -> StringDict[AnyField]:
    return dict(fetch_fields_iterator(base))


# import cycle solution
from gd.memory.base import Struct
