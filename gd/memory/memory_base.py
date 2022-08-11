from typing import Any, Optional, Type, TypeVar

from gd.memory.fields import AnyField
from gd.memory.memory import Memory, MemoryType
from gd.platform import SYSTEM_PLATFORM_CONFIG, PlatformConfig
from gd.typing import AnyType, DynamicTuple, Namespace, StringDict

__all__ = ("MemoryAbstractType", "MemoryAbstract", "MemoryStruct", "MemoryUnion")

MAT = TypeVar("MAT", bound="MemoryAbstractType")


class MemoryAbstractType(MemoryType):
    _fields: StringDict[AnyField]

    def __new__(
        cls: Type[MAT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        size: int = 0,
        alignment: int = 0,
        fields: Optional[StringDict[AnyField]] = None,
        config: PlatformConfig = SYSTEM_PLATFORM_CONFIG,
        **keywords: Any,
    ) -> MAT:
        self = super().__new__(
            cls,
            name,
            bases,
            namespace,
            size=size,
            alignment=alignment,
            config=config,
            **keywords,
        )

        if fields is None:
            fields = {}

        self._fields = fields

        return self

    @property
    def fields(cls) -> StringDict[AnyField]:
        return cls._fields


class MemoryAbstract(Memory, metaclass=MemoryAbstractType):
    pass


class MemoryStruct(MemoryAbstract):
    pass


class MemoryUnion(MemoryAbstract):
    pass
