from typing import (
    Any,
    Generic,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
    overload,
)

from attrs import define, field, frozen

from gd.memory.markers import AnyMarker
from gd.memory.memory import Memory
from gd.memory.traits import Layout, Read, ReadWrite
from gd.typing import AnyType, StringDict, is_instance

__all__ = ("Field", "MutField", "FieldMarker", "MutFieldMarker", "field", "mut_field")

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

    def __get__(
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


@frozen()
class FieldMarker:
    pass


def field() -> FieldMarker:
    return FieldMarker()


@frozen()
class MutFieldMarker(FieldMarker):
    pass


def mut_field() -> MutFieldMarker:
    return MutFieldMarker()


Fields = StringDict[Tuple[Type[AnyMarker], FieldMarker]]
FieldsIterator = Iterator[Tuple[str, Tuple[Type[AnyMarker], FieldMarker]]]


def fetch_fields_from(base: AnyType) -> FieldsIterator:
    type_hints = get_type_hints(base)

    for name, maybe in vars(base).items():
        if is_instance(maybe, FieldMarker):
            yield (name, (type_hints[name], maybe))


def fetch_fields_iter(type: AnyType) -> FieldsIterator:
    for base in reversed(type.mro()):
        yield from fetch_fields_from(base)


def fetch_fields(type: AnyType) -> Fields:
    return dict(fetch_fields_iter(type))
