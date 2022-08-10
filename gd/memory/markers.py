from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Type, TypeVar
from typing import Union as TypeUnion

from typing_extensions import Never
from gd.memory.context import Context

from gd.memory.traits import Layout
from gd.memory.utils import set_name
from gd.platform import PlatformConfig
from gd.typing import AnyType, DynamicTuple, Namespace, get_name

if TYPE_CHECKING:
    from gd.memory.memory import Memory
    from gd.memory.memory_arrays import MemoryArray, MemoryMutArray
    from gd.memory.memory_base import MemoryStruct, MemoryUnion
    from gd.memory.memory_pointers_refs import (
        MemoryMutPointer, MemoryMutRef, MemoryPointer, MemoryRef
    )
    from gd.memory.memory_special import MemoryThis, MemoryVoid
    from gd.memory.state import AbstractState
    from gd.memory.visitor import Visitor

__all__ = (
    "SimpleMarker",
    "Marker",
    "Array",
    "MutArray",
    "array",
    "mut_array",
    "Pointer",
    "MutPointer",
    "pointer",
    "mut_pointer",
    "Ref",
    "MutRef",
    "ref",
    "mut_ref",
    "DynamicFill",
    "dynamic_fill",
    "fill",
    "Struct",
    "Union",
    "This",
    "this",
    "Void",
    "void",
    "byte_t",
    "ubyte_t",
    "short_t",
    "ushort_t",
    "int_t",
    "uint_t",
    "long_t",
    "ulong_t",
    "longlong_t",
    "ulonglong_t",
    "int8_t",
    "uint8_t",
    "int16_t",
    "uint16_t",
    "int32_t",
    "uint32_t",
    "int64_t",
    "uint64_t",
    "intptr_t",
    "uintptr_t",
    "intsize_t",
    "uintsize_t",
    "float_t",
    "double_t",
    "float32_t",
    "float64_t",
    "bool_t",
    "char_t",
    "string_t",
)


class SimpleMarkerType(type):
    def __repr__(cls) -> str:
        return get_name(cls)

    @property
    def name(cls) -> str:
        return get_name(cls)


CAN_NOT_INITIALIZE_SIMPLE_MARKERS = "simple markers can not be initialized"


class SimpleMarker(metaclass=SimpleMarkerType):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[Memory]:
        return visitor.visit_simple(cls)

    def __init__(self) -> Never:
        raise TypeError(CAN_NOT_INITIALIZE_SIMPLE_MARKERS)


# C INT TYPES


class byte_t(SimpleMarker):
    pass


class ubyte_t(SimpleMarker):
    pass


class short_t(SimpleMarker):
    pass


class ushort_t(SimpleMarker):
    pass


class int_t(SimpleMarker):
    pass


class uint_t(SimpleMarker):
    pass


class long_t(SimpleMarker):
    pass


class ulong_t(SimpleMarker):
    pass


class longlong_t(SimpleMarker):
    pass


class ulonglong_t(SimpleMarker):
    pass


# INT TYPES


class int8_t(SimpleMarker):
    pass


class uint8_t(SimpleMarker):
    pass


class int16_t(SimpleMarker):
    pass


class uint16_t(SimpleMarker):
    pass


class int32_t(SimpleMarker):
    pass


class uint32_t(SimpleMarker):
    pass


class int64_t(SimpleMarker):
    pass


class uint64_t(SimpleMarker):
    pass


# POINTER / SIZE TYPES


class intptr_t(SimpleMarker):
    pass


class uintptr_t(SimpleMarker):
    pass


class intsize_t(SimpleMarker):
    pass


class uintsize_t(SimpleMarker):
    pass


# C FLOAT TYPES


class float_t(SimpleMarker):
    pass


class double_t(SimpleMarker):
    pass


# FLOAT TYPES


class float32_t(SimpleMarker):
    pass


class float64_t(SimpleMarker):
    pass


# BOOL TYPE


class bool_t(SimpleMarker):
    pass


# CHAR TYPE


class char_t(SimpleMarker):
    pass


# STRING TYPE


class string_t(SimpleMarker):
    pass


class Marker:
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[Layout]:
        return visitor.visit(cls)

    @classmethod
    def create(cls, config: PlatformConfig) -> Type[Layout]:
        from gd.memory.visitor import Visitor

        return Visitor(Context(config)).visit(cls)

    @classmethod
    def bound(cls, state: AbstractState) -> Type[Layout]:
        from gd.memory.visitor import Visitor

        visitor = Visitor.bound(state)

        return visitor.visit(cls)


class Union(Marker):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryUnion]:
        return visitor.visit_union(cls)


STT = TypeVar("STT", bound="StructType")


class StructType(type):
    _vtable: bool
    _packed: bool
    _origin: int

    def __new__(
        cls: Type[STT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        vtable: bool = False,
        packed: bool = False,
        origin: int = 0,
        **keywords: Any,
    ) -> STT:
        self = super().__new__(cls, name, bases, namespace, **keywords)

        self._vtable = vtable
        self._packed = packed
        self._origin = origin

        return self

    @property
    def vtable(cls) -> bool:
        return cls._vtable

    @property
    def packed(cls) -> bool:
        return cls._packed

    @property
    def origin(cls) -> int:
        return cls._origin


class Struct(Marker, metaclass=StructType):
    _vtable: bool
    _packed: bool
    _origin: int

    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryStruct]:
        return visitor.visit_struct(cls)

    @property
    def vtable(self) -> bool:
        return self._vtable

    @property
    def packed(self) -> bool:
        return self._packed

    @property
    def origin(self) -> int:
        return self._origin


ST = TypeVar("ST", bound="SpecialType")

CAN_NOT_CREATE_SPECIAL = "can not create special types"


class SpecialType(type):
    def __new__(
        cls: Type[ST],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        special: bool = False,
        **keywords: Any,
    ) -> ST:
        if not special:
            raise TypeError(CAN_NOT_CREATE_SPECIAL)

        return super().__new__(cls, name, bases, namespace, **keywords)


S = TypeVar("S", bound="Special")

CAN_NOT_INSTANTIATE = "can not instantiate {}"


class Special(Marker, metaclass=SpecialType, special=True):
    def __init__(self) -> Never:
        raise TypeError(CAN_NOT_INSTANTIATE.format(get_name(type(self))))


class Void(Special, special=True):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryVoid]:
        return visitor.visit_void(cls)


void = Void


class This(Special, special=True):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryThis]:
        return visitor.visit_this(cls)


this = This


APT = TypeVar("APT", bound="AbstractPointerType")


class AbstractPointerType(type):
    _type: Type[AnyMarker]
    _signed: bool

    def __new__(
        cls: Type[APT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        type: Type[AnyMarker] = void,
        **keywords: Any,
    ) -> APT:
        self = super().__new__(cls, name, bases, namespace, **keywords)

        self._type = type

        return self  # type: ignore

    def new(self: APT, type: Type[AnyMarker] = void) -> APT:
        class pointer(self, type=type):
            pass

        set_name(pointer, get_name(self))

        return pointer

    @property
    def type(self) -> Type[AnyMarker]:
        return self._type


class AbstractPointer(Marker, metaclass=AbstractPointerType):
    _type: Type[AnyMarker]

    @property
    def type(self) -> Type[AnyMarker]:
        return self._type


class Pointer(AbstractPointer):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryPointer]:
        return visitor.visit_pointer(cls)


class MutPointer(Pointer):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryMutPointer]:
        return visitor.visit_mut_pointer(cls)


def pointer(type: Type[AnyMarker] = void) -> Type[Pointer]:
    return Pointer.new(type)


def mut_pointer(type: Type[AnyMarker] = void) -> Type[MutPointer]:
    return MutPointer.new(type)


class Ref(Pointer):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryRef]:
        return visitor.visit_ref(cls)


class MutRef(Ref, MutPointer):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryMutRef]:
        return visitor.visit_mut_ref(cls)


def ref(type: Any) -> Type[Ref]:
    return Ref.new(type)


def mut_ref(type: Any) -> Type[MutRef]:
    return MutRef.new(type)


AAT = TypeVar("AAT", bound="AbstractArrayType")


class AbstractArrayType(type):
    _type: Type[AnyMarker]
    _length: Optional[int]

    def __new__(
        cls: Type[AAT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        type: Type[AnyMarker] = void,
        length: Optional[int] = None,
        **keywords: Any,
    ) -> AAT:
        self = super().__new__(cls, name, bases, namespace, **keywords)

        self._type = type

        self._length = length

        return self

    def new(self: AAT, type: Type[AnyMarker] = void, length: Optional[int] = None) -> AAT:
        class array(self, type=type, length=length):
            pass

        set_name(array, get_name(self))

        return array

    @property
    def type(self) -> Type[AnyMarker]:
        return self._type

    @property
    def length(self) -> Optional[int]:
        return self._length


class AbstractArray(Marker, metaclass=AbstractArrayType):
    _type: Type[AnyMarker]
    _length: Optional[int]

    @property
    def type(self) -> Type[AnyMarker]:
        return self._type

    @property
    def length(self) -> Optional[int]:
        return self._length


class Array(AbstractArray):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryArray]:
        return visitor.visit_array(cls)


class MutArray(Array):
    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryMutArray]:
        return visitor.visit_mut_array(cls)


def array(type: Type[AnyMarker] = void, length: Optional[int] = None) -> Type[Array]:
    return Array.new(type, length)


def mut_array(type: Type[AnyMarker] = void, length: Optional[int] = None) -> Type[MutArray]:
    return MutArray.new(type, length)


Fills = Dict[PlatformConfig, int]


DFT = TypeVar("DFT", bound="DynamicFillType")


class DynamicFillType(type):
    _fills: Fills

    def __new__(
        cls: Type[DFT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        fills: Optional[Fills] = None,
        **keywords: Any,
    ) -> DFT:
        self = super().__new__(cls, name, bases, namespace, **keywords)

        if fills is None:
            fills = {}

        self._fills = fills

        return self

    def new(self: DFT, **keywords: int) -> DFT:
        fills = {PlatformConfig.from_string(string): fill for string, fill in keywords.items()}

        class dynamic_fill(self, fills=fills):
            pass

        set_name(dynamic_fill, get_name(self))

        return dynamic_fill

    @property
    def fills(self) -> Fills:
        return self._fills


class DynamicFill(Marker, metaclass=DynamicFillType):
    _fills: Fills

    @classmethod
    def accept(cls, visitor: Visitor) -> Type[MemoryArray]:
        return visitor.visit_dynamic_fill(cls)

    @property
    def fills(self) -> Fills:
        return self._fills


def dynamic_fill(**keywords: int) -> Type[DynamicFill]:
    return DynamicFill.new(**keywords)


def fill(length: int) -> Type[Array]:
    return array(char_t, length)


AnyMarker = TypeUnion[SimpleMarker, Marker]
