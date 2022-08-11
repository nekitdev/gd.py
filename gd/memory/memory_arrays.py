from sys import maxsize as max_size
from typing import Any, Generic, Iterable, Iterator, Optional, Type, TypeVar, Union, overload

from gd.memory.memory import Memory, MemoryType
from gd.memory.memory_special import MemoryVoid
from gd.memory.traits import Layout, Read, ReadWrite
from gd.platform import SYSTEM_PLATFORM_CONFIG, PlatformConfig
from gd.typing import AnyType, DynamicTuple, Namespace, is_instance

__all__ = ("MemoryAbstractArrayType", "MemoryArray", "MemoryMutArray")

MAAT = TypeVar("MAAT", bound="MemoryAbstractArrayType")

UNSIZED_ARRAY = "array is unsized"


class MemoryAbstractArrayType(MemoryType):
    _type: Type[Layout]
    _length: Optional[int]

    def __new__(
        cls: Type[MAAT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        type: Type[Layout] = MemoryVoid,
        length: Optional[int] = None,
        config: PlatformConfig = SYSTEM_PLATFORM_CONFIG,
        **keywords: Any,
    ) -> MAAT:
        self = super().__new__(cls, name, bases, namespace, config=config, **keywords)

        self._type = type

        self._length = length

        return self

    @property
    def size(self) -> int:
        if self.length is None:
            raise TypeError(UNSIZED_ARRAY)

        return self.type.size * self.length

    @property
    def alignment(self) -> int:
        return self.type.alignment

    @property
    def type(self) -> Type[Layout]:
        return self._type

    @property
    def length(self) -> Optional[int]:
        return self._length


L = TypeVar("L", bound=Layout)


class MemoryAbstractArray(Generic[L], Memory, metaclass=MemoryAbstractArrayType):
    _type: Type[L]
    _length: Optional[int]

    def __len__(self) -> int:
        self.check_length()

        return self.length  # type: ignore

    @property
    def type(self) -> Type[L]:
        return self._type

    @property
    def length(self) -> Optional[int]:
        return self._length

    def check_length(self) -> None:
        if self.length is None:
            raise TypeError(UNSIZED_ARRAY)

    def calculate_address(self, index: int) -> int:
        return self.address + index * self.type.size


T = TypeVar("T")

INDEX_OUT_OF_BOUNDS = "the index is out of bounds"


class MemoryArray(MemoryAbstractArray[Read[T]]):
    @overload  # noqa
    def __getitem__(self, item: int) -> T:  # noqa
        ...

    @overload  # noqa
    def __getitem__(self, item: slice) -> Iterator[T]:  # noqa
        ...

    def __getitem__(self, item: Union[int, slice]) -> Union[T, Iterator[T]]:  # noqa
        if is_instance(item, int):
            return self.read_at(item)

        start, stop, step = item.indices(self.length or max_size)

        return self.iter_read(range(start, stop, step))

    def read_at(self, index: int) -> T:
        if self.length is None or index < self.length:
            return self.type.read_value_from(self.state, self.calculate_address(index))

        raise IndexError(INDEX_OUT_OF_BOUNDS)

    def iter_read(self, indexes: Iterable[int]) -> Iterator[T]:
        for index in indexes:
            yield self.read_at(index)

    def read(self) -> Iterator[T]:
        self.check_length()

        return self.iter_read(range(self.length))  # type: ignore


class MemoryMutArray(MemoryArray[T], MemoryAbstractArray[ReadWrite[T]]):
    @overload  # noqa
    def __setitem__(self, item: int, value: T) -> None:  # noqa
        ...

    @overload  # noqa
    def __setitem__(self, item: slice, value: Iterable[T]) -> None:  # noqa
        ...

    def __setitem__(self, item: Union[int, slice], value: Union[T, Iterable[T]]) -> None:  # noqa
        if is_instance(item, int):
            return self.write_at(item, value)  # type: ignore

        start, stop, step = item.indices(self.length or max_size)

        return self.iter_write(range(start, stop, step), value)  # type: ignore

    def write_at(self, index: int, value: T) -> None:
        if self.length is None or index < self.length:
            self.type.write_value_to(value, self.state, self.calculate_address(index))

        else:
            raise IndexError(INDEX_OUT_OF_BOUNDS)

    def iter_write(self, indexes: Iterable[int], values: Iterable[T]) -> None:
        for index, value in zip(indexes, values):
            self.write_at(index, value)

    def write(self, values: Iterable[T]) -> None:
        for index, value in enumerate(values):
            self.write_at(index, value)
