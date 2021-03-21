# DOCUMENT

from gd.memory.utils import class_property
from gd.platform import Platform, system_bits, system_platform
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Any, Dict, Generic, Tuple, Type, TypeVar, Union

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("MemoryType", "Memory")

M = TypeVar("M", bound="Memory")


class MemoryType(type(Generic)):  # type: ignore
    _bits: int
    _platform: Platform
    _size: int
    _alignment: int

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        size: int = 0,
        alignment: int = 0,
        bits: int = system_bits,
        platform: Union[int, str, Platform] = system_platform,
        **kwargs,
    ) -> "MemoryType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, **kwargs)

        cls._size = size  # type: ignore
        cls._alignment = alignment  # type: ignore

        cls._bits = bits  # type: ignore
        cls._platform = Platform.from_value(platform)  # type: ignore

        return cls  # type: ignore

    @property
    def size(cls) -> int:
        return cls._size

    @property
    def alignment(cls) -> int:
        return cls._alignment

    @property
    def bits(cls) -> int:
        return cls._bits

    @property
    def platform(cls) -> Platform:
        return cls._platform


class Memory(metaclass=MemoryType):
    _bits: int
    _platform: Platform
    _size: int
    _alignment: int

    def __init__(self, state: "BaseState", address: int) -> None:
        self._state = state
        self._address = address

    def __repr__(self) -> str:
        info = {"address": hex(self.address), "state": self.state}

        return make_repr(self, info)

    @class_property
    def size(self) -> int:
        return self._size

    @class_property
    def alignment(self) -> int:
        return self._alignment

    @class_property
    def bits(self) -> int:
        return self._bits

    @class_property
    def platform(self) -> Platform:
        return self._platform

    @property
    def state(self) -> "BaseState":
        return self._state

    @property
    def address(self) -> int:
        return self._address

    @classmethod
    def read_from(cls: Type[M], state: "BaseState", address: int) -> M:
        return cls(state, address)

    @classmethod
    def read_value_from(cls: Type[M], state: "BaseState", address: int) -> M:
        return cls(state, address)
