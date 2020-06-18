import ctypes
import functools
import inspect

from gd.typing import Any, Dict, Function, List, Tuple, Type

FuncPtr = ctypes._CFuncPtr


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


def func_def(func_ptr: FuncPtr) -> FuncPtr:
    def wrap(func: Function) -> Function:
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
        def handle_call(*args, **kwargs) -> Any:
            return func_ptr(*parse_args_and_kwargs(func, *args, **kwargs))

        return handle_call

    return wrap


def parse_args_and_kwargs(func: Function, *args, **kwargs) -> List[Any]:
    """Parses kwargs into positional args, assuming that args are at the beginning.
    This does not support variadic arguments.
    """
    names = list(inspect.signature(func).parameters.keys())

    final_name_args = inspect.getcallargs(func, *args, **kwargs)
    # we are doing this because args are not guaranteed to be in order
    final_args = [None] * len(names)

    for name, arg in final_name_args.items():
        final_args[names.index(name)] = arg

    return final_args
