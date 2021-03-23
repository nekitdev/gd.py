# DOCUMENT

from gd.iter_utils import item_to_tuple
from gd.memory.memory import Memory
from gd.memory.utils import class_property
from gd.platform import Platform, platform_from_string, system_bits, system_platform
from gd.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union as TypeUnion,
    cast,
    no_type_check,
)

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa
    from gd.memory.visitor import Visitor  # noqa

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
        return cls.__name__

    @property
    def name(cls) -> str:
        return cls.__name__


class SimpleMarker(metaclass=SimpleMarkerType):
    def __init__(self) -> None:
        raise TypeError("Markers can not be initialized.")


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


class MarkerType(type(Generic)):  # type: ignore
    _derive: bool

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = True,
        **kwargs,
    ) -> "MarkerType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, **kwargs)

        cls._derive = derive  # type: ignore

        return cls

        # return no_type_check(cls)  # type: ignore

    def assert_can_derive(cls) -> None:
        if not cls.derive:
            raise TypeError(f"Can not derive memory from {cls.__name__}.")

    def visit(cls, visitor: "Visitor") -> Type[Memory]:
        cls.assert_can_derive()

        return cast(Type[Memory], visitor.visit_any(cls))

    def create(
        cls, bits: int = system_bits, platform: TypeUnion[int, str, Platform] = system_platform
    ) -> Type[Memory]:
        from gd.memory.visitor import Visitor

        visitor = Visitor.with_context(bits, Platform.from_value(platform))

        return cls.visit(visitor)

    def bound(cls, state: "BaseState") -> Type[Memory]:
        from gd.memory.visitor import Visitor

        visitor = Visitor.bound(state)

        return cls.visit(visitor)

    def __getitem__(cls, item: Any) -> Type[Memory]:
        return cls.create(*item_to_tuple(item))

    @property
    def derive(cls) -> bool:
        return cls._derive


class Marker(metaclass=MarkerType):
    _derive: bool

    @class_property
    def derive(self) -> bool:
        return self._derive


class PointerType(MarkerType):
    _type: Any
    _signed: bool

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = True,
        type: Optional[Any] = None,
        signed: bool = False,
        **kwargs,
    ) -> "PointerType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, derive=derive, **kwargs)

        if type is not None:
            cls._type = type  # type: ignore

        cls._signed = signed  # type: ignore

        return cls  # type: ignore

    def __repr__(cls) -> str:
        try:
            return f"{cls.__name__}({cls.type!r})"

        except AttributeError:
            return cls.__name__

    @no_type_check
    def new(cls, type: Any, signed: bool = False) -> "PointerType":
        class pointer(cls, type=type, signed=signed):
            pass

        pointer.__qualname__ = pointer.__name__ = cls.__name__

        return pointer

    @property
    def type(cls) -> Any:
        return cls._type

    @property
    def signed(cls) -> bool:
        return cls._signed


class PointerBase(Marker, metaclass=PointerType):
    _type: Any
    _signed: bool

    @class_property
    def type(self) -> Any:
        return self._type

    @class_property
    def signed(self) -> bool:
        return self._signed


class Pointer(PointerBase):
    pass


class MutPointer(Pointer):
    pass


def pointer(type: Any, signed: bool = False) -> Type[Pointer]:
    return Pointer.new(type, signed=signed)


def mut_pointer(type: Any, signed: bool = False) -> Type[MutPointer]:
    return MutPointer.new(type, signed=signed)


class Ref(Pointer):
    pass


class MutRef(Ref, MutPointer):
    pass


def ref(type: Any, signed: bool = False) -> Type[Ref]:
    return Ref.new(type, signed=signed)


def mut_ref(type: Any, signed: bool = False) -> Type[MutRef]:
    return MutRef.new(type, signed=signed)


class ArrayType(MarkerType):
    _type: Any
    _length: Optional[int]

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = True,
        type: Optional[Any] = None,
        length: Optional[int] = None,
        **kwargs,
    ) -> "ArrayType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, derive=derive, **kwargs)

        if type is not None:
            cls._type = type  # type: ignore

        cls._length = length  # type: ignore

        return cls  # type: ignore

    def __repr__(cls) -> str:
        try:
            if cls.length is None:
                return f"{cls.__name__}({cls.type!r})"

            return f"{cls.__name__}({cls.type!r}, {cls.length})"

        except AttributeError:
            return cls.__name__

    @no_type_check
    def new(cls, type: Any, length: Optional[int] = None) -> "ArrayType":
        class array(cls, type=type, length=length):
            pass

        array.__qualname__ = array.__name__ = cls.__name__

        return array

    @property
    def type(cls) -> Any:
        return cls._type

    @property
    def length(cls) -> Optional[int]:
        return cls._length


class ArrayBase(Marker, metaclass=ArrayType, derive=False):
    _type: Any
    _length: Optional[int]

    @class_property
    def type(self) -> Any:
        self._type

    @class_property
    def length(self) -> Optional[int]:
        return self._length


class Array(ArrayBase, derive=False):
    pass


class MutArray(Array, derive=False):
    pass


def array(type: Any, length: Optional[int] = None) -> Type[Array]:
    return Array.new(type, length)


def mut_array(type: Any, length: Optional[int] = None) -> Type[MutArray]:
    return MutArray.new(type, length)


class DynamicFillType(MarkerType):
    _fill: Dict[Tuple[int, Platform], int]

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = True,
        fill: Optional[Dict[Tuple[int, Platform], int]] = None,
        **kwargs,
    ) -> "DynamicFillType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, **kwargs)

        if fill is None:
            fill = {}

        cls._fill = fill  # type: ignore

        return cls

    @no_type_check
    def new(cls, **fills: int) -> "DynamicFillType":
        class offset(
            cls, fill={platform_from_string(string): fill for string, fill in fills.items()}
        ):
            pass

        offset.__qualname__ = offset.__name__ = cls.__name__

        return offset

    @property
    def fill(self) -> Dict[Tuple[int, Platform], int]:
        return self._fill


class DynamicFill(Marker, metaclass=DynamicFillType):
    _fill: Dict[Tuple[int, Platform], int]

    @class_property
    def fill(self) -> Dict[Tuple[int, Platform], int]:
        return self._fill


def dynamic_fill(**fills: int) -> Type[DynamicFill]:
    return DynamicFill.new(**fills)


def fill(length: int) -> Type[Array]:
    return array(char_t, length)


class Union(Marker, metaclass=MarkerType, derive=False):
    pass


class StructType(MarkerType):
    _vtable: bool
    _packed: bool
    _origin: int

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = True,
        vtable: bool = False,
        packed: bool = False,
        origin: int = 0,
        **kwargs,
    ) -> "StructType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, derive=derive, **kwargs)

        cls._vtable = vtable  # type: ignore
        cls._packed = packed  # type: ignore
        cls._origin = origin  # type: ignore

        return cls

    @property
    def vtable(cls) -> bool:
        return cls._vtable

    @property
    def packed(cls) -> bool:
        return cls._packed

    @property
    def origin(cls) -> int:
        return cls._origin


class Struct(Marker, metaclass=StructType, derive=False):
    _vtable: bool
    _packed: bool
    _origin: int

    @class_property
    def vtable(self) -> bool:
        return self._vtable

    @class_property
    def packed(self) -> bool:
        return self._packed

    @class_property
    def origin(self) -> int:
        return self._origin


class SpecialType(MarkerType):
    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = False,
        special: bool = False,
        **kwargs,
    ) -> "SpecialType":
        if not special:
            raise TypeError("Can not derive from this type.")

        return super().__new__(meta_cls, cls_name, bases, cls_dict, derive=derive, **kwargs)


S = TypeVar("S", bound="Special")


class Special(Marker, metaclass=SpecialType, special=True, derive=False):
    def __new__(cls: Type[S], *ignored_args, **ignored_kwargs) -> S:
        raise TypeError(f"Can not instantiate {cls.__name__}.")


class Void(Special, special=True, derive=False):
    pass


void = Void


class This(Special, special=True, derive=False):
    pass


this = This
