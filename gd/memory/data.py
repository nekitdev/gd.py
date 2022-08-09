from __future__ import annotations

from struct import calcsize as compute_size
from struct import pack, unpack
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Type, TypeVar

from attrs import define

from gd.constants import EMPTY
from gd.enums import ByteOrder
from gd.iter_utils import contains_only_item
from gd.memory.utils import bits
from gd.typing import AnyType, DynamicTuple, Namespace

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = ("Data", "DataType")

T = TypeVar("T")


class DataType(type(Generic)):  # type: ignore
    _name: str
    _format: str
    _size: int
    _alignment: int
    _order: ByteOrder

    def __new__(
        cls: Type[DT],
        type_name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        name: str = EMPTY,
        format: str = EMPTY,
        alignment: int = 0,
        **keywords: Any,
    ) -> DT:
        self = super().__new__(cls, type_name, bases, namespace, **keywords)

        size = compute_size(format)

        self._name = name
        self._format = format
        self._size = size
        self._alignment = alignment or size

        return self

    @property
    def name(cls) -> str:
        return cls._name

    @property
    def format(cls) -> str:
        return cls._format

    @property
    def size(cls) -> int:
        return cls._size

    @property
    def alignment(cls) -> int:
        return cls._alignment

    @property
    def bits(cls) -> int:
        return bits(cls.size)

    @property
    def order(self) -> ByteOrder:
        return self._order

    @property
    def pack_format(cls) -> str:
        return cls.order.value + cls.format


DT = TypeVar("DT", bound=DataType)

D = TypeVar("D", bound="AnyData")


@define()
class Data(Generic[T], metaclass=DataType):
    _name: ClassVar[str] = EMPTY
    _format: ClassVar[str] = EMPTY
    _size: ClassVar[int] = 0
    _alignment: ClassVar[int] = 0
    _order: ClassVar[ByteOrder] = ByteOrder.NATIVE

    value: T

    @classmethod
    def read_from(cls: Type[D], state: AbstractState, address: int) -> D:
        return cls(cls.read_value_from(state, address))

    @classmethod
    def read_value_from(cls, state: AbstractState, address: int) -> T:
        result = unpack(cls.pack_format, state.read_at(address, cls.size))

        if contains_only_item(result):
            (result,) = result

        return result  # type: ignore

    def write_to(self, state: AbstractState, address: int) -> None:
        self.write_value_to(self.value, state, address)

    @classmethod
    def write_value_to(cls, value: T, state: AbstractState, address: int) -> None:
        state.write_at(address, pack(cls.pack_format, value))


AnyData = Data[Any]
