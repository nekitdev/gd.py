from __future__ import annotations

from builtins import setattr as set_attribute
from ctypes import Structure as CTypesStruct
from ctypes import Union as CTypesUnion
from typing import Any, Type, TypeVar, get_type_hints

from funcs.decorators import wraps
from typing_aliases import AnyCallable, AnyType, DecoratorIdentity, DynamicTuple, Namespace
from typing_extensions import Never

__all__ = ("Struct", "Union", "external", "unimplemented")

UNIMPLEMENTED = "this function is not implemented"


def unimplemented(*args: Any, **kwargs: Any) -> Never:
    raise NotImplementedError(UNIMPLEMENTED)


FIELDS = "_fields_"

Bases = DynamicTuple[AnyType]

CS = TypeVar("CS", bound="StructType")


class StructType(type(CTypesStruct)):  # type: ignore
    def __new__(cls: Type[CS], name: str, bases: DynamicTuple[AnyType], namespace: Namespace) -> CS:
        self = super().__new__(cls, name, bases, namespace)

        fields = get_type_hints(self)

        set_attribute(self, FIELDS, list(fields.items()))

        return self  # type: ignore


CU = TypeVar("CU", bound="UnionType")


class UnionType(type(CTypesUnion)):  # type: ignore
    def __new__(cls: Type[CU], name: str, bases: DynamicTuple[AnyType], namespace: Namespace) -> CU:
        self = super().__new__(cls, name, bases, namespace)

        fields = get_type_hints(self)

        set_attribute(self, FIELDS, list(fields.items()))

        return self  # type: ignore


class Struct(CTypesStruct, metaclass=StructType):
    """Represents `struct` types that have the ability to populate their fields with annotations."""


class Union(CTypesUnion, metaclass=UnionType):
    """Represents `union` types that have the ability to populate their fields with annotations."""


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
        def handle_call(*args: Any) -> Any:  # type: ignore
            return function_pointer(*args)

        return handle_call

    return wrap
