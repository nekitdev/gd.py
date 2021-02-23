from gd.memory.memory import MemoryType, Memory
from gd.platform import Platform, system_bits, system_platform
from gd.typing import Any, Dict, Tuple, Type, Union

__all__ = ("VOID_SIZE", "MemoryVoidType", "MemoryVoid")

VOID_SIZE = 0


class MemoryVoidType(MemoryType):
    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        bits: int = system_bits,
        platform: Union[int, str, Platform] = system_platform,
        **kwargs,
    ) -> "MemoryVoidType":
        return super().__new__(
            meta_cls,
            cls_name,
            bases,
            cls_dict,
            size=VOID_SIZE,
            bits=bits,
            platform=platform,
            **kwargs,
        )


class MemoryVoid(Memory, metaclass=MemoryVoidType):
    def __init_subclass__(cls, _root: bool = False, **ignored) -> None:
        if not _root:
            raise TypeError("Can not derive from void.")
