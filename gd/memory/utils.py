import ctypes
from typing import Any, Dict, Tuple, Type


class StructureMeta(type(ctypes.Structure)):
    def __new__(
        meta_cls, name: str, bases: Tuple[Type[Any]], namespace: Dict[str, Any]
    ) -> Type[ctypes.Structure]:
        cls = super().__new__(meta_cls, name, bases, namespace)

        fields = {}

        for base in reversed(cls.mro()):
            try:
                fields.update(cls.__annotations__)
            except AttributeError:
                pass

        cls._fields_ = list(fields.items())

        return cls


class Structure(ctypes.Structure, metaclass=StructureMeta):
    """Structure that has ability to populate its fields with annotations."""

    pass
