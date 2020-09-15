import ctypes
import functools

from gd.typing import Any, Callable, Dict, Tuple, Type, TypeVar

T = TypeVar("T")


class StructureMeta(type(ctypes.Structure)):  # type: ignore
    def __new__(  # type: ignore
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

        return cls  # type: ignore


class Structure(ctypes.Structure, metaclass=StructureMeta):
    """Structure that has ability to populate its fields with annotations."""

    pass


def func_def(func_ptr: Any) -> Any:
    def wrap(func: Callable[..., T]) -> Callable[..., T]:
        try:
            annotations = func.__annotations__

        except AttributeError:
            pass

        else:
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
