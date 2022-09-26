from __future__ import annotations

from builtins import setattr as set_attribute
from ctypes import Structure as CStructure
from ctypes import Union as CUnion
from functools import wraps
from typing import Any, Type, TypeVar, get_type_hints

from gd.typing import AnyCallable, AnyType, DecoratorIdentity, DynamicTuple, Namespace

__all__ = (
    "Structure",
    "Union",
    "external",
    "set_name",
    "set_module",
)


def set_name(item: Any, name: str) -> None:
    item.__qualname__ = item.__name__ = name


def set_module(item: Any, module: str) -> None:
    item.__module__ = module


FIELDS = "_fields_"


class StructureType(type(CStructure)):  # type: ignore
    def __new__(cls: Type[CS], name: str, bases: DynamicTuple[AnyType], namespace: Namespace) -> CS:
        self = super().__new__(cls, name, bases, namespace)

        fields = get_type_hints(self)

        set_attribute(self, FIELDS, list(fields.items()))

        return self


CS = TypeVar("CS", bound=StructureType)


class UnionType(type(CUnion)):  # type: ignore
    def __new__(cls: Type[CU], name: str, bases: DynamicTuple[AnyType], namespace: Namespace) -> CU:
        self = super().__new__(cls, name, bases, namespace)

        fields = get_type_hints(self)

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


def external(function_pointer: Any) -> DecoratorIdentity[AnyCallable]:
    def wrap(function: AnyCallable) -> AnyCallable:
        annotations = get_type_hints(function)

        return_type = annotations.pop(RETURN, None)

        if return_type:
            set_attribute(function_pointer, RETURN_TYPE, return_type)

        argument_types = list(annotations.values())

        if argument_types:
            set_attribute(function_pointer, ARGUMENT_TYPES, argument_types)

        @wraps(function)
        def handle_call(*args: Any) -> Any:
            return function_pointer(*args)

        return handle_call

    return wrap
