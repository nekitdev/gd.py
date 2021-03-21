# DOCUMENT

import sys

from gd.iter_utils import is_iterable
from gd.memory.memory import MemoryType, Memory
from gd.memory.traits import Layout, ReadLayout, ReadWriteLayout
from gd.memory.utils import class_property
from gd.platform import Platform, system_bits, system_platform
from gd.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("MemoryArrayType", "MemoryArray", "MemoryMutArray")

L = TypeVar("L", bound=Layout)
T = TypeVar("T")


class MemoryArrayType(MemoryType):
    _type: Type[Layout]
    _length: Optional[int]

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        type: Optional[Type[Layout]] = None,
        length: Optional[int] = None,
        bits: int = system_bits,
        platform: Union[int, str, Platform] = system_platform,
        **kwargs,
    ) -> "MemoryArrayType":
        cls = super().__new__(
            meta_cls, cls_name, bases, cls_dict, bits=bits, platform=platform, **kwargs
        )

        if type is not None:
            cls._type = type  # type: ignore

        cls._length = length  # type: ignore

        return cls  # type: ignore

    @property
    def size(cls) -> int:
        if cls.length is None:
            raise TypeError("Array is unsized.")

        return cls.type.size * cls.length

    @property
    def alignment(cls) -> int:
        return cls.type.alignment

    @property
    def type(cls) -> Type[Layout]:
        return cls._type

    @property
    def length(cls) -> Optional[int]:
        return cls._length


class MemoryBaseArray(Generic[L], Memory, metaclass=MemoryArrayType):
    _type: Type[L]
    _length: Optional[int]

    def __init__(self, state: "BaseState", address: int) -> None:
        self._state = state
        self._address = address

    def __len__(self) -> int:
        if self.length is None:
            raise TypeError("Array is unsized.")

        return self.length

    def calculate_address(self, index: int) -> int:
        return self.address + index * self.type.size

    @class_property
    def type(self) -> Type[L]:  # type: ignore
        return self._type

    @class_property
    def size(self) -> int:
        if self.length is None:
            raise TypeError("Array is unsized.")

        return self.type.size * self.length

    @class_property
    def alignment(self) -> int:
        return self.type.alignment

    @class_property
    def length(self) -> Optional[int]:
        return self._length

    @property
    def state(self) -> "BaseState":
        return self._state

    @property
    def address(self) -> int:
        return self._address


class MemoryArray(MemoryBaseArray[ReadLayout[T]]):
    _type: Type[ReadLayout[T]]  # type: ignore

    @class_property
    def type(self) -> Type[ReadLayout[T]]:  # type: ignore
        return self._type

    @overload  # noqa
    def __getitem__(self, item: int) -> T:  # noqa
        ...

    @overload  # noqa
    def __getitem__(self, item: slice) -> Iterator[T]:  # noqa
        ...

    def __getitem__(self, item: Union[int, slice]) -> Union[T, Iterator[T]]:  # noqa
        if isinstance(item, int):
            return self.read_at(item)

        if isinstance(item, slice):
            start, stop, step = item.indices(self.length or sys.maxsize)

            return self.read_iter(range(start, stop, step))

        raise TypeError("Expected either slices or integer indexes.")

    def read_at(self, index: int) -> T:
        if self.length is None or index < self.length:
            return self.type.read_value_from(self.state, self.calculate_address(index))

        raise IndexError("Index is out of bounds.")

    def read_iter(self, index_iter: Iterable[int]) -> Iterator[T]:
        for index in index_iter:
            yield self.read_at(index)

    def read(self) -> Iterator[T]:
        if self.length is None:
            raise TypeError("Array is unsized.")

        return self.read_iter(range(self.length))


class MemoryMutArray(MemoryArray[T], MemoryBaseArray[ReadWriteLayout[T]]):
    _type: Type[ReadWriteLayout[T]]  # type: ignore

    @class_property
    def type(self) -> Type[ReadWriteLayout[T]]:  # type: ignore
        return self._type

    @overload  # noqa
    def __setitem__(self, item: int, value: T) -> None:  # noqa
        ...

    @overload  # noqa
    def __setitem__(self, item: slice, value: Iterable[T]) -> None:  # noqa
        ...

    def __setitem__(  # noqa
        self, item: Union[int, slice], value: Union[T, Iterable[T]]
    ) -> None:
        if isinstance(item, int):
            return self.write_at(item, cast(T, value))

        if isinstance(item, slice):
            if is_iterable(value):
                start, stop, step = item.indices(self.length or sys.maxsize)

                return self.write_iter(
                    range(start, stop, step), cast(Iterable[T], value)
                )

            raise ValueError("Expected iterable value with slices.")

        raise TypeError("Expected either slices or integer indexes.")

    def write_at(self, index: int, value: T) -> None:
        if self.length is None or index < self.length:
            return self.type.write_value_to(value, self.state, self.calculate_address(index))

        raise IndexError("Index is out of bounds.")

    def write_iter(self, index_iter: Iterable[int], value_iter: Iterable[T]) -> None:
        for index, value in zip(index_iter, value_iter):
            self.write_at(index, value)

    def write(self, values: Iterable[T]) -> None:
        for index, value in enumerate(values):
            self.write_at(index, value)
