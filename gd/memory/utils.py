from __future__ import annotations

from builtins import setattr as set_attribute
from ctypes import Structure as CStructure
from ctypes import Union as CUnion
from functools import wraps
from math import ceil, log2
from typing import Any, Callable, Optional, Type, TypeVar, get_type_hints

from gd.binary_utils import BITS
from gd.typing import AnyType, Binary, DecoratorIdentity, DynamicTuple, Namespace, Unary

__all__ = (
    "Structure", "Union", "bits", "closest_power_of_two", "closest_power_of_two_bits", "external"
)


S = TypeVar("S")
T = TypeVar("T")


def class_property(
    get_function: Optional[Unary[S, T]] = None,
    set_function: Optional[Binary[S, T, None]] = None,
    delete_function: Optional[Unary[S, None]] = None,
) -> T:
    return property(get_function, set_function, delete_function)  # type: ignore


def bits(size: int) -> int:
    return size * BITS


def closest_power_of_two_bits(value: int) -> int:
    return ceil(log2(value))


def closest_power_of_two(value: int) -> int:
    return 1 << closest_power_of_two_bits(value)


FIELDS = "_fields_"


class StructureType(type(CStructure)):  # type: ignore
    def __new__(cls: Type[CS], name: str, bases: DynamicTuple[AnyType], namespace: Namespace) -> CS:
        self = super().__new__(cls, name, bases, namespace)

        fields = {}

        for base in reversed(self.mro()):
            fields.update(get_type_hints(base))

        set_attribute(self, FIELDS, list(fields.items()))

        return self


CS = TypeVar("CS", bound=StructureType)


class UnionType(type(CUnion)):  # type: ignore
    def __new__(cls: Type[CU], name: str, bases: DynamicTuple[AnyType], namespace: Namespace) -> CU:
        self = super().__new__(cls, name, bases, namespace)

        fields = {}

        for base in reversed(self.mro()):
            fields.update(get_type_hints(base))

        set_attribute(self, FIELDS, list(fields.items()))

        return self


CU = TypeVar("CU", bound=UnionType)


class Structure(CStructure, metaclass=StructureType):
    """Represents structures that have ability to populate their fields with annotations."""


class Union(CUnion, metaclass=UnionType):
    """Represents unions that have ability to populate their fields with annotations."""


RETURN = "return"

ARGUMENT_TYPES = "argtypes"
RETURN_TYPE = "restype"


def external(function_pointer: Any) -> DecoratorIdentity[Callable[..., Any]]:
    def wrap(function: Callable[..., Any]) -> Callable[..., Any]:
        annotations = get_type_hints(function)

        return_type = annotations.pop(RETURN, None)

        if return_type:
            set_attribute(function_pointer, RETURN_TYPE, return_type)

        argument_types = list(annotations.values())

        if argument_types:
            set_attribute(function_pointer, ARGUMENT_TYPES, return_type)

        @wraps(function)
        def handle_call(*args: Any) -> Any:
            return function_pointer(*args)

        return handle_call

    return wrap
