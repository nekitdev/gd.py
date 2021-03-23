# DOCUMENT

from gd.memory.memory import MemoryType, Memory
from gd.platform import Platform, system_bits, system_platform
from gd.typing import Any, Dict, Tuple, Type, Union

__all__ = ("SPECIAL_SIZE", "MemorySpecialType", "MemorySpecial", "MemoryThis", "MemoryVoid")

SPECIAL_SIZE = 0
SPECIAL_ALIGNMENT = 0


class MemorySpecialType(MemoryType):
    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        bits: int = system_bits,
        platform: Union[int, str, Platform] = system_platform,
        **kwargs,
    ) -> "MemorySpecialType":
        return super().__new__(
            meta_cls,
            cls_name,
            bases,
            cls_dict,
            size=SPECIAL_SIZE,
            alignment=SPECIAL_ALIGNMENT,
            bits=bits,
            platform=platform,
            **kwargs,
        )


class MemorySpecial(Memory, metaclass=MemorySpecialType):
    pass


class MemoryThis(MemorySpecial):
    pass


class MemoryVoid(MemorySpecial):
    pass
