from typing import Any, Type, TypeVar

from gd.memory.memory import Memory, MemoryType
from gd.platform import SYSTEM_PLATFORM_CONFIG, PlatformConfig
from gd.typing import AnyType, DynamicTuple, Namespace

__all__ = ("SPECIAL_SIZE", "MemorySpecialType", "MemorySpecial", "MemoryThis", "MemoryVoid")

SPECIAL_SIZE = 0
SPECIAL_ALIGNMENT = 0

MST = TypeVar("MST", bound="MemorySpecialType")


class MemorySpecialType(MemoryType):
    def __new__(
        cls: Type[MST],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        config: PlatformConfig = SYSTEM_PLATFORM_CONFIG,
        **keywords: Any,
    ) -> MST:
        return super().__new__(
            cls,
            name,
            bases,
            namespace,
            size=SPECIAL_SIZE,
            alignment=SPECIAL_ALIGNMENT,
            config=config,
            **keywords,
        )


class MemorySpecial(Memory, metaclass=MemorySpecialType):
    pass


class MemoryThis(MemorySpecial):
    pass


class MemoryVoid(MemorySpecial):
    pass
