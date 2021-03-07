import ctypes
import functools

from gd.typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, cast, get_type_hints

T = TypeVar("T")

__all__ = ("Structure", "Union", "bits", "closest_power_of_two", "extern_fn")


def class_property(
    get_function: Optional[Callable[..., T]] = None,
    set_function: Optional[Callable[..., None]] = None,
    del_function: Optional[Callable[..., None]] = None,
) -> T:
    return cast(T, property(get_function, set_function, del_function))


def bits(size: int, *, byte_bits: int = 8) -> int:
    return size * byte_bits


def closest_power_of_two(value: int) -> int:
    result = 1

    while result < value:
        result *= 2

    return result


class StructureMeta(type(ctypes.Structure)):  # type: ignore
    def __new__(  # type: ignore
        meta_cls, name: str, bases: Tuple[Type[Any], ...], namespace: Dict[str, Any]
    ) -> Type[ctypes.Structure]:
        cls = super().__new__(meta_cls, name, bases, namespace)

        fields = {}

        for base in reversed(cls.mro()):
            fields.update(get_type_hints(base))

        cls._fields_ = list(fields.items())

        return cls  # type: ignore


class UnionMeta(type(ctypes.Union)):  # type: ignore
    def __new__(  # type: ignore
        meta_cls, name: str, bases: Tuple[Type[Any], ...], namespace: Dict[str, Any]
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


def extern_fn(function_pointer: Any) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def wrap(function: Callable[..., T]) -> Callable[..., T]:
        annotations = get_type_hints(function)

        return_type = annotations.pop("return", None)

        if return_type:
            function_pointer.restype = return_type

        argument_types = list(annotations.values())

        if argument_types:
            function_pointer.argtypes = argument_types

        @functools.wraps(function)
        def handle_call(*args) -> T:
            return function_pointer(*args)

        return handle_call

    return wrap
