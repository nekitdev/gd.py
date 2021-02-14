from gd.iter_utils import item_to_tuple
from gd.memory.data import Data
from gd.memory.traits import Read, Write, Sized, is_class, is_sized
from gd.memory.types import Types
from gd.memory.utils import class_property
from gd.platform import Platform, system_bits, system_platform
from gd.text_utils import make_repr
from gd.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_type_hints,
    overload,
)

if TYPE_CHECKING:
    from gd.memory.state import BaseState

__all__ = (
    "Marker",
    "MarkerBase",
    "MarkerStruct",
    "MarkerUnion",
    "MemoryBase",
    "MemoryStruct",
    "MemoryUnion",
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
)

M = TypeVar("M", bound="MemoryBase")
S = TypeVar("S", bound="Sized")
T = TypeVar("T")


class Marker:
    def __init__(self, name: str) -> None:
        self._name = name

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name


byte_t = Marker("byte_t")
ubyte_t = Marker("ubyte_t")
short_t = Marker("short_t")
ushort_t = Marker("ushort_t")
int_t = Marker("int_t")
uint_t = Marker("uint_t")
long_t = Marker("long_t")
ulong_t = Marker("ulong_t")
longlong_t = Marker("longlong_t")
ulonglong_t = Marker("ulonglong_t")

int8_t = Marker("int8_t")
uint8_t = Marker("uint8_t")
int16_t = Marker("int16_t")
uint16_t = Marker("uint16_t")
int32_t = Marker("int32_t")
uint32_t = Marker("uint32_t")
int64_t = Marker("int64_t")
uint64_t = Marker("uint64_t")

intptr_t = Marker("intptr_t")
uintptr_t = Marker("uintptr_t")
intsize_t = Marker("intsize_t")
uintsize_t = Marker("uintsize_t")

float_t = Marker("float_t")
double_t = Marker("double_t")

float32_t = Marker("float32_t")
float64_t = Marker("float64_t")

bool_t = Marker("bool_t")


class ReadSized(Read[T], Sized):
    pass


class ReadWriteSized(Read[T], Write[T], Sized):
    pass


class BaseField(Generic[S]):
    def __init__(self, type: Type[S], offset: int) -> None:
        self._type = type
        self._offset = offset

    def __repr__(self) -> str:
        info = {"offset": self.offset, "size": self.size, "type": self.type.__name__}

        return make_repr(self, info)

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def type(self) -> Type[S]:
        return self._type

    @property
    def size(self) -> int:
        return self.type.size


class Field(BaseField[ReadSized[T]]):
    def __init__(self, type: Type[ReadSized[T]], offset: int) -> None:
        super().__init__(type, offset)

    @overload  # noqa
    def __get__(  # noqa
        self, instance: Literal[None], owner: Optional[Type[Any]] = None
    ) -> "Field[T]":
        ...

    @overload  # noqa
    def __get__(self, instance: Any, owner: Optional[Type[Any]] = None) -> T:  # noqa
        ...

    def __get__(  # noqa
        self, instance: Optional[Any], owner: Optional[Type[Any]] = None
    ) -> Union[T, "Field[T]"]:
        if instance is None:
            return self

        return instance.state.read_value(self.type, instance.address + self.offset)

    def __set__(self, instance: Any, value: T) -> None:
        raise AttributeError("Can not set field, as it is immutable.")

    def __delete__(self, instance: Any) -> None:
        raise AttributeError("Can not delete field.")


class MutField(Field[T], BaseField[ReadWriteSized[T]]):
    def __init__(self, type: Type[ReadWriteSized[T]], offset: int) -> None:
        super().__init__(type, offset)  # type: ignore

    def __set__(self, instance: Any, value: T) -> None:
        instance.state.write_value(self.type, value, instance.address)

    def __delete__(self, instance: Any) -> None:
        raise AttributeError("Can not delete field.")


class Context:
    def __init__(
        self,
        bits: int,
        platform: Platform = system_platform,
        offset: int = 0,
        size: int = 0,
    ) -> None:
        self._bits = bits
        self._platform = platform

        self._offset = offset
        self._size = size

    def __repr__(self) -> str:
        info = {
            "bits": self.bits,
            "platform": self.platform.name.casefold(),
            "offset": self.offset,
            "size": self.size,
        }

        return make_repr(self, info)

    @property
    def bits(self) -> int:
        return self._bits

    @property
    def platform(self) -> Platform:
        return self._platform

    def get_offset(self) -> int:
        return self._offset

    def set_offset(self, offset: int) -> None:
        self._offset = offset

    offset = property(get_offset, set_offset)

    def get_size(self) -> int:
        return self._size

    def set_size(self, size: int) -> None:
        self._size = size

    size = property(get_size, set_size)

    @property
    def types(self) -> Types:
        return Types(self.bits, self.platform)

    def create_field(self, type: Type[ReadSized[T]], offset: Optional[int] = None) -> Field[T]:
        if offset is None:
            offset = self.offset

        return Field(type, offset)

    def create_mut_field(
        self, type: Type[ReadWriteSized[T]], offset: Optional[int] = None
    ) -> MutField[T]:
        if offset is None:
            offset = self.offset

        return MutField(type, offset)

    def get_type(self, name: str) -> Type[Data[Any]]:
        return self.types.get(name)


class MemoryType(type):
    _fields: Dict[str, Field]
    _bits: int
    _platform: Platform
    _size: int

    @class_property
    def size(cls) -> int:
        return cls._size

    @class_property
    def fields(cls) -> Dict[str, Field]:
        return cls._fields

    @class_property
    def bits(cls) -> int:
        return cls._bits

    @class_property
    def platform(cls) -> Platform:
        return cls._platform


class MemoryBase(metaclass=MemoryType):
    _fields: Dict[str, Field]
    _bits: int
    _platform: Platform
    _size: int

    def __init__(self, state: "BaseState", address: int) -> None:
        self._state = state
        self._address = address

    def __repr__(self) -> str:
        info = {"address": hex(self.address), "state": self.state}

        return make_repr(self, info)

    @class_property
    def size(self) -> int:
        return self._size

    @class_property
    def fields(self) -> Dict[str, Field]:
        return self._fields

    @class_property
    def bits(self) -> int:
        return self._bits

    @class_property
    def platform(self) -> Platform:
        return self._platform

    @property
    def type(self) -> MemoryType:
        return type(self)

    @property
    def state(self) -> "BaseState":
        return self._state

    @property
    def address(self) -> int:
        return self._address

    @classmethod
    def read(cls: Type[M], state: "BaseState", address: int) -> M:
        return cls.read_value(state, address)

    @classmethod
    def read_value(cls: Type[M], state: "BaseState", address: int) -> M:
        return cls(state, address)


class MemoryStruct(MemoryBase):
    pass


class MemoryUnion(MemoryBase):
    pass


class MarkerType(type):
    _derive: bool
    _offset: int

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = True,
        offset: int = 0,
    ) -> "MarkerType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        cls._derive = derive  # type: ignore
        cls._offset = offset  # type: ignore

        return cls  # type: ignore

    def create(
        cls, bits: int = system_bits, platform: Union[int, str, Platform] = system_platform
    ) -> Type[MemoryBase]:
        if not cls._derive:
            raise TypeError(f"Can not derive memory from {cls.__name__}.")

        ctx = Context(
            bits=bits, platform=Platform.from_value(platform), offset=cls._offset
        )

        return visit_any(ctx, cls, return_field=False)

    def __getitem__(cls, item: Any) -> Type[MemoryBase]:
        return cls.create(*item_to_tuple(item))

    @class_property
    def derive(cls) -> bool:
        return cls._derive

    @class_property
    def offset(cls) -> int:
        return cls._offset


class MarkerBase(metaclass=MarkerType, derive=False):
    _derive: bool
    _offset: int

    @class_property
    def derive(self) -> bool:
        return self._derive

    @class_property
    def offset(self) -> int:
        return self._offset


class MarkerStruct(MarkerBase, derive=False):
    pass


class MarkerUnion(MarkerBase, derive=False):
    pass


@overload  # noqa
def visit_any(ctx: Context, some: Any, return_field: Literal[True]) -> Field[T]:  # noqa
    ...


@overload  # noqa
def visit_any(ctx: Context, some: Any, return_field: Literal[False]) -> Type[MemoryBase]:  # noqa
    ...


@overload  # noqa
def visit_any(  # noqa
    ctx: Context, some: Any, return_field: bool
) -> Union[Type[MemoryBase], Field[T]]:
    ...


def visit_any(  # noqa
    ctx: Context, some: Any, return_field: bool = True
) -> Union[Type[MemoryBase], Field[T]]:
    if is_class(some):
        if issubclass(some, MarkerStruct):
            return visit_struct(ctx, cast(Type[MarkerStruct], some), return_field=return_field)

        if issubclass(some, MarkerUnion):
            return visit_union(ctx, cast(Type[MarkerUnion], some), return_field=return_field)

        if is_sized(some):
            if issubclass(some, Read):
                if not return_field:
                    raise ValueError("Expected return_field to be true.")

                if issubclass(some, Write):
                    return visit_read_write_sized(ctx, some)

                return visit_read_sized(ctx, some)

    if not return_field:
        raise ValueError("Expected return_field to be true.")

    if isinstance(some, Marker):
        return visit_marker(ctx, some)

    if isinstance(some, str):
        return visit_name(ctx, some)

    raise TypeError(f"{some!r} is not valid as type for fields.")


@overload  # noqa
def visit_struct(  # noqa
    ctx: Context, marker_struct: Type[MarkerStruct], return_field: Literal[True]
) -> Field[T]:
    ...


@overload  # noqa
def visit_struct(  # noqa
    ctx: Context, marker_struct: Type[MarkerStruct], return_field: Literal[False]
) -> Type[MemoryStruct]:
    ...


@overload  # noqa
def visit_struct(  # noqa
    ctx: Context, marker_struct: Type[MarkerStruct], return_field: bool
) -> Union[Type[MemoryStruct], Field[T]]:
    ...


def visit_struct(  # noqa
    ctx: Context, marker_struct: Type[MarkerStruct], return_field: bool = True
) -> Union[Type[MemoryStruct], Field[T]]:
    fields: Dict[str, Field] = {}

    size = 0

    for name, annotation in get_type_hints(marker_struct).items():
        try:
            field = visit_any(ctx, annotation)  # type: ignore

        except TypeError:
            continue

        if name in fields:
            raise ValueError(f"Repeated field: {name!r}.")

        fields[name] = field

        ctx.offset += field.size
        size += field.size

    ctx.size += size

    class struct(MemoryStruct):
        pass

    name = marker_struct.__name__

    struct.__qualname__ = struct.__name__ = name

    struct._fields = fields
    struct._size = size
    struct._bits = ctx.bits
    struct._platform = ctx.platform

    for name, field in fields.items():
        if hasattr(struct, name):
            raise ValueError(f"Field has invalid name: {name!r}.")

        setattr(struct, name, field)

    if return_field:
        return visit_read_sized(ctx, cast(Type[ReadSized[struct]], struct))  # type: ignore

    return struct


@overload  # noqa
def visit_union(  # noqa
    ctx: Context, marker_union: Type[MarkerUnion], return_field: Literal[True]
) -> Field[T]:
    ...


@overload  # noqa
def visit_union(  # noqa
    ctx: Context, marker_union: Type[MarkerUnion], return_field: Literal[False]
) -> Type[MemoryUnion]:
    ...


@overload  # noqa
def visit_union(  # noqa
    ctx: Context, marker_union: Type[MarkerUnion], return_field: bool
) -> Union[Type[MemoryUnion], Field[T]]:
    ...


def visit_union(  # noqa
    ctx: Context, marker_union: Type[MarkerUnion], return_field: bool = True
) -> Union[Type[MemoryUnion], Field[T]]:
    fields: Dict[str, Field] = {}

    size = 0

    for name, annotation in get_type_hints(marker_union).items():
        try:
            field = visit_any(ctx, annotation)  # type: ignore

        except TypeError:
            continue

        if name in fields:
            raise ValueError(f"Repeated field: {name!r}.")

        fields[name] = field

        field_size = field.size

        if field_size > size:
            size = field_size

    ctx.offset += size
    ctx.size += size

    class union(MemoryUnion):
        pass

    name = marker_union.__name__

    union.__qualname__ = union.__name__ = name

    union._fields = fields
    union._size = size
    union._bits = ctx.bits
    union._platform = ctx.platform

    for name, field in fields.items():
        if hasattr(union, name):
            raise ValueError(f"Field has invalid name: {name!r}.")

        setattr(union, name, field)

    if return_field:
        return visit_read_sized(ctx, cast(Type[ReadSized[union]], union))  # type: ignore

    return union


def visit_read_sized(ctx: Context, type: Type[ReadSized[T]]) -> Field[T]:
    return ctx.create_field(type)


def visit_read_write_sized(ctx: Context, type: Type[ReadWriteSized[T]]) -> MutField[T]:
    return ctx.create_mut_field(type)


def visit_marker(ctx: Context, marker: Marker) -> MutField[T]:
    return visit_name(ctx, marker.name)


def visit_name(ctx: Context, name: str) -> MutField[T]:
    return visit_read_write_sized(ctx, cast(Type[ReadWriteSized[T]], ctx.get_type(name)))
