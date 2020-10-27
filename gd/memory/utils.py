import ctypes
import functools

from gd.typing import Any, Callable, Dict, Tuple, Type, TypeVar, get_type_hints

T = TypeVar("T")

__all__ = ("Structure", "Union", "extern_func")


class StructureMeta(type(ctypes.Structure)):  # type: ignore
    def __new__(  # type: ignore
        meta_cls, name: str, bases: Tuple[Type[Any]], namespace: Dict[str, Any]
    ) -> Type[ctypes.Structure]:
        cls = super().__new__(meta_cls, name, bases, namespace)

        fields = {}

        for base in reversed(cls.mro()):
            fields.update(get_type_hints(base))

        cls._fields_ = list(fields.items())

        return cls  # type: ignore


class UnionMeta(type(ctypes.Union)):  # type: ignore
    def __new__(  # type: ignore
        meta_cls, name: str, bases: Tuple[Type[Any]], namespace: Dict[str, Any]
    ) -> Type[ctypes.Union]:
        cls = super().__new__(meta_cls, name, bases, namespace)

        fields = {}

        for base in reversed(cls.mro()):
            fields.update(get_type_hints(base))

        cls._fields_ = list(fields.items())

        return cls  # type: ignore


class Structure(ctypes.Structure, metaclass=StructureMeta):
    """Structure that has ability to populate its fields with annotations."""

    pass


class Union(ctypes.Union, metaclass=UnionMeta):
    """Union that has ability to populate its fields with annotations."""

    pass


def extern_func(func_ptr: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def wrap(func: Callable[..., T]) -> Callable[..., T]:
        annotations = get_type_hints(func)

        return_type = annotations.pop("return", None)

        if return_type:
            func_ptr.restype = return_type

        arg_types = list(annotations.values())

        if arg_types:
            func_ptr.argtypes = arg_types

        @functools.wraps(func)
        def handle_call(*args) -> T:
            return func_ptr(*args)

        return handle_call

    return wrap
