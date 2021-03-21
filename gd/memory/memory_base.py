# DOCUMENT

from gd.memory.field import Field
from gd.memory.memory import MemoryType, Memory
from gd.memory.utils import class_property
from gd.platform import Platform, system_bits, system_platform
from gd.typing import Any, Dict, Optional, Tuple, Type, Union

__all__ = ("MemoryBaseType", "MemoryBase", "MemoryStruct", "MemoryUnion")


class MemoryBaseType(MemoryType):
    _fields: Dict[str, Field]

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        size: int = 0,
        alignment: int = 0,
        fields: Optional[Dict[str, Field]] = None,
        bits: int = system_bits,
        platform: Union[int, str, Platform] = system_platform,
        **kwargs,
    ) -> "MemoryBaseType":
        cls = super().__new__(
            meta_cls,
            cls_name,
            bases,
            cls_dict,
            size=size,
            alignment=alignment,
            bits=bits,
            platform=platform,
            **kwargs,
        )

        if fields is None:
            fields = {}

        cls._fields = fields  # type: ignore

        return cls  # type: ignore

    @property
    def fields(cls) -> Dict[str, Field]:
        return cls._fields


class MemoryBase(Memory, metaclass=MemoryBaseType):
    _fields: Dict[str, Field]

    @class_property
    def fields(self) -> Dict[str, Field]:
        return self._fields


class MemoryStruct(MemoryBase):
    pass


class MemoryUnion(MemoryBase):
    pass
