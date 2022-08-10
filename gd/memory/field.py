from typing import Any, Generic, Optional, Type, TypeVar, Union, overload

from attrs import define, field

from gd.memory.memory import Memory
from gd.memory.traits import Layout, Read, ReadWrite

__all__ = ("Field", "MutField")

L = TypeVar("L", bound=Layout)
T = TypeVar("T")

FROZEN_FIELD = "this field is frozen"


@define()
class AbstractField(Generic[L]):
    _type: Type[L] = field()
    _offset: int = field(default=0)
    _frozen: bool = field(default=False, init=False)

    def get_type(self) -> Type[L]:
        return self._type

    def set_type(self, type: Type[L]) -> None:
        self.check_frozen()

        self._type = type

    type = property(get_type, set_type)

    def get_offset(self) -> int:
        return self._offset

    def set_offset(self, offset: int) -> None:
        self.check_frozen()

        self._offset = offset

    offset = property(get_offset, set_offset)

    def check_frozen(self) -> None:
        if self._frozen:
            raise TypeError(FROZEN_FIELD)

    def freeze(self) -> None:
        self._frozen = True

    def unfreeze(self) -> None:
        self._frozen = False


M = TypeVar("M", bound="Memory")

F = TypeVar("F", bound="AnyField")

CAN_NOT_SET_IMMUTABLE = "can not set an immutable field"
CAN_NOT_DELETE_FIELDS = "can not delete fields"


class Field(Generic[T], AbstractField[Read[T]]):
    @overload
    def __get__(self: F, instance: None, type: Optional[Type[M]] = ...) -> F:
        ...

    @overload
    def __get__(self, instance: M, type: Optional[Type[M]] = ...) -> T:
        ...

    def __get__(  # noqa
        self: F, instance: Optional[M], type: Optional[Type[M]] = None
    ) -> Union[T, F]:
        if instance is None:
            return self

        return self.type.read_value_from(instance.state, instance.address + self.offset)

    def __set__(self, instance: M, value: T) -> None:
        raise AttributeError(CAN_NOT_SET_IMMUTABLE)

    def __delete__(self, instance: M) -> None:
        raise AttributeError(CAN_NOT_DELETE_FIELDS)


AnyField = Field[Any]


class MutField(Field[T], AbstractField[ReadWrite[T]]):
    def __set__(self, instance: M, value: T) -> None:
        self.type.write_value_to(value, instance.state, instance.address + self.offset)
