from gd.iter_utils import item_to_tuple
from gd.memory.memory import Memory
from gd.memory.utils import class_property
from gd.platform import Platform, system_bits, system_platform
from gd.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Optional,
    Tuple,
    Type,
    Union as TypeUnion,
    cast,
    no_type_check,
)

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa
    from gd.memory.visitor import Visitor  # noqa

__all__ = (
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
    "Struct",
    "Union",
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
)


class MarkerMeta(type):
    def __repr__(cls) -> str:
        return cls.__name__

    @property
    def name(cls) -> str:
        return cls.__name__


class Marker(metaclass=MarkerMeta):
    def __init__(self) -> None:
        raise TypeError("Markers can not be initialized.")


# C INT TYPES

class byte_t(Marker):
    pass


class ubyte_t(Marker):
    pass


class short_t(Marker):
    pass


class ushort_t(Marker):
    pass


class int_t(Marker):
    pass


class uint_t(Marker):
    pass


class long_t(Marker):
    pass


class ulong_t(Marker):
    pass


class longlong_t(Marker):
    pass


class ulonglong_t(Marker):
    pass


# INT TYPES

class int8_t(Marker):
    pass


class uint8_t(Marker):
    pass


class int16_t(Marker):
    pass


class uint16_t(Marker):
    pass


class int32_t(Marker):
    pass


class uint32_t(Marker):
    pass


class int64_t(Marker):
    pass


class uint64_t(Marker):
    pass


# POINTER / SIZE TYPES

class intptr_t(Marker):
    pass


class uintptr_t(Marker):
    pass


class intsize_t(Marker):
    pass


class uintsize_t(Marker):
    pass


# C FLOAT TYPES

class float_t(Marker):
    pass


class double_t(Marker):
    pass


# FLOAT TYPES

class float32_t(Marker):
    pass


class float64_t(Marker):
    pass


# BOOL TYPE

class bool_t(Marker):
    pass


# CHAR TYPE

class char_t(Marker):
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
    ) -> "PointerType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, derive=derive)

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


class Pointer(metaclass=PointerType):
    _type: Any
    _signed: bool

    @class_property
    def type(self) -> Any:
        return self._type

    @class_property
    def signed(self) -> bool:
        return self._signed


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
    ) -> "ArrayType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, derive=derive)

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


class ArrayBase(metaclass=ArrayType, derive=False):
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


class BaseType(MarkerType):
    pass


class Base(metaclass=BaseType, derive=False):
    pass


class Struct(Base, derive=False):
    pass


class Union(Base, derive=False):
    pass
