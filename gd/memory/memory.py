from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Optional, Type, TypeVar

from attrs import define, field

from gd.platform import PlatformConfig
from gd.typing import AnyType, DynamicTuple, Namespace

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = ("MemoryType", "Memory")

MT = TypeVar("MT", bound="MemoryType")


class MemoryType(type(Generic)):  # type: ignore
    _config: PlatformConfig
    _size: int
    _alignment: int

    def __new__(
        cls: Type[MT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        size: int = 0,
        alignment: int = 0,
        config: Optional[PlatformConfig] = None,
        **keywords: Any,
    ) -> MT:
        self = super().__new__(cls, name, bases, namespace, **keywords)

        self._size = size
        self._alignment = alignment or size

        if config is None:
            config = PlatformConfig.system()

        self._config = config

        return self

    @property
    def size(self) -> int:
        return self._size

    @property
    def alignment(self) -> int:
        return self._alignment

    @property
    def config(self) -> PlatformConfig:
        return self._config


M = TypeVar("M", bound="Memory")


@define()
class Memory(metaclass=MemoryType):
    state: AbstractState = field()
    address: int = field(repr=hex)

    @classmethod
    def read_from(cls: Type[M], state: AbstractState, address: int) -> M:
        return cls(state, address)

    @classmethod
    def read_value_from(cls: Type[M], state: AbstractState, address: int) -> M:
        return cls(state, address)
