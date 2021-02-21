from gd.iter_utils import is_iterable, item_to_tuple
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
    Iterable,
    Iterator,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union as TypeUnion,
    cast,
    get_type_hints,
    no_type_check,
    overload,
)

if TYPE_CHECKING:
    from gd.memory.state import BaseState

__all__ = (
    "Marker",
    "Struct",
    "Union",
    "Array",
    "MutArray",
    "Memory",
    "MemoryArray",
    "MemoryMutArray",
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

ANNOTATIONS = "__annotations__"

M = TypeVar("M", bound="Memory")
S = TypeVar("S", bound="Sized")
T = TypeVar("T")


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
    ) -> TypeUnion[T, "Field[T]"]:
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

    def get_type(self, name: str) -> Type[Sized]:
        return self.types.get(name)


class MemoryType(type):
    _bits: int
    _platform: Platform
    _size: int

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        size: int = 0,
        bits: int = system_bits,
        platform: TypeUnion[int, str, Platform] = system_platform,
    ) -> "MemoryType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        cls._size = size  # type: ignore

        cls._bits = bits  # type: ignore
        cls._platform = Platform.from_value(platform)  # type: ignore

        return cls  # type: ignore

    @property
    def size(cls) -> int:
        return cls._size

    @property
    def bits(cls) -> int:
        return cls._bits

    @property
    def platform(cls) -> Platform:
        return cls._platform


class MemoryBaseType(MemoryType):
    _fields: Dict[str, Field]

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        size: int = 0,
        fields: Optional[Dict[str, Field]] = None,
        bits: int = system_bits,
        platform: TypeUnion[int, str, Platform] = system_platform,
    ) -> "MemoryBaseType":
        cls = super().__new__(
            meta_cls, cls_name, bases, cls_dict, size=size, bits=bits, platform=platform
        )

        if fields is None:
            fields = {}

        cls._fields = fields  # type: ignore

        return cls  # type: ignore

    @property
    def fields(cls) -> Dict[str, Field]:
        return cls._fields


class Memory(metaclass=MemoryType):
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
    def bits(self) -> int:
        return self._bits

    @class_property
    def platform(self) -> Platform:
        return self._platform

    @property
    def type(self: M) -> Type[M]:
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


class MemoryArrayType(MemoryType):
    _type: Type[Sized]
    _length: Optional[int]

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        type: Optional[Type[Sized]] = None,
        length: Optional[int] = None,
        bits: int = system_bits,
        platform: TypeUnion[int, str, Platform] = system_platform,
    ) -> "MemoryArrayType":
        cls = super().__new__(
            meta_cls, cls_name, bases, cls_dict, bits=bits, platform=platform
        )

        if type is not None:
            cls._type = type  # type: ignore

        cls._length = length  # type: ignore

        return cls  # type: ignore

    @property
    def size(cls) -> int:
        if cls.length is None:
            raise TypeError("Array is unsized.")

        return cls.type.size * cls.length

    @property
    def type(cls) -> Type[Sized]:
        return cls._type

    @property
    def length(cls) -> Optional[int]:
        return cls._length


class MemoryBaseArray(Generic[S], Memory, metaclass=MemoryArrayType):
    _type: Type[S]
    _length: Optional[int]

    def __init__(self, state: "BaseState", address: int) -> None:
        self._state = state
        self._address = address

    def __len__(self) -> int:
        if self.length is None:
            raise TypeError("Array is unsized.")

        return self.length

    def calculate_address(self, index: int) -> int:
        return self.address + index * self.type.size

    @class_property
    def type(self) -> Type[S]:  # type: ignore
        return self._type

    @class_property
    def length(self) -> Optional[int]:
        return self._length

    @property
    def state(self) -> "BaseState":
        return self._state

    @property
    def address(self) -> int:
        return self._address


class MemoryArray(MemoryBaseArray[ReadSized[T]]):
    _type: Type[ReadSized[T]]  # type: ignore

    @class_property
    def type(self) -> Type[ReadSized[T]]:  # type: ignore
        return self._type

    @overload  # noqa
    def __getitem__(self, item: int) -> T:  # noqa
        ...

    @overload  # noqa
    def __getitem__(self, item: slice) -> Iterator[T]:  # noqa
        ...

    def __getitem__(self, item: TypeUnion[int, slice]) -> TypeUnion[T, Iterator[T]]:  # noqa
        if isinstance(item, int):
            return self.read_at(item)

        if isinstance(item, slice):
            return self.read_iter(range(item.start, item.stop, item.step))

        raise TypeError("Expected either slices or integer indexes.")

    def read_at(self, index: int) -> T:
        if self.length is None or index < self.length:
            return self.state.read_value(self.type, self.calculate_address(index))

        raise IndexError("Index is out of bounds.")

    def read_iter(self, index_iter: Iterable[int]) -> Iterator[T]:
        for index in index_iter:
            yield self.read_at(index)


class MemoryMutArray(MemoryArray[T], MemoryBaseArray[ReadWriteSized[T]]):
    _type: Type[ReadWriteSized[T]]  # type: ignore

    @class_property
    def type(self) -> Type[ReadWriteSized[T]]:  # type: ignore
        return self._type

    @overload  # noqa
    def __setitem__(self, item: int, value: T) -> None:  # noqa
        ...

    @overload  # noqa
    def __setitem__(self, item: slice, value: Iterable[T]) -> None:  # noqa
        ...

    def __setitem__(  # noqa
        self, item: TypeUnion[int, slice], value: TypeUnion[T, Iterable[T]]
    ) -> None:
        if isinstance(item, int):
            return self.write_at(item, cast(T, value))

        if isinstance(item, slice):
            if is_iterable(value):
                return self.write_iter(
                    range(item.start, item.stop, item.step), cast(Iterable[T], value)
                )

            raise ValueError("Expected iterable value with slices.")

        raise TypeError("Expected either slices or integer indexes.")

    def write_at(self, index: int, value: T) -> None:
        if self.length is None or index < self.length:
            return self.state.write_value(self.type, value, self.calculate_address(index))

        raise IndexError("Index is out of bounds.")

    def write_iter(self, index_iter: Iterable[int], value_iter: Iterable[T]) -> None:
        for index, value in zip(index_iter, value_iter):
            self.write_at(index, value)


class MemoryBase(Memory, metaclass=MemoryBaseType):
    _fields: Dict[str, Field]

    @class_property
    def fields(self) -> Dict[str, Field]:
        return self._fields


class MemoryStruct(MemoryBase):
    pass


class MemoryUnion(MemoryBase):
    pass


class MarkerType(type):
    _derive: bool

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        derive: bool = True,
    ) -> "MarkerType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        cls._derive = derive  # type: ignore

        return cls  # type: ignore

    def create(
        cls, bits: int = system_bits, platform: TypeUnion[int, str, Platform] = system_platform
    ) -> Type[Memory]:
        if not cls.derive:
            raise TypeError(f"Can not derive memory from {cls.__name__}.")

        ctx = Context(bits=bits, platform=Platform.from_value(platform))

        return cast(Type[Memory], visit_any(ctx, cls))

    def __getitem__(cls, item: Any) -> Type[Memory]:
        return cls.create(*item_to_tuple(item))

    @property
    def derive(cls) -> bool:
        return cls._derive


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
    def __call__(cls, type: Any, length: Optional[int] = None) -> "ArrayType":
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
    _type: Optional[Any]
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


class MarkerBase(metaclass=MarkerType, derive=False):
    _derive: bool

    @class_property
    def derive(self) -> bool:
        return self._derive


class Struct(MarkerBase, derive=False):
    pass


class Union(MarkerBase, derive=False):
    pass


def visit_any(ctx: Context, some: Any) -> Type[Sized]:
    if is_class(some):
        if issubclass(some, Struct):
            return visit_struct(ctx, cast(Type[Struct], some))

        if issubclass(some, Union):
            return visit_union(ctx, cast(Type[Union], some))

        if issubclass(some, Array):
            if issubclass(some, MutArray):
                return visit_mut_array(ctx, some)

            return visit_array(ctx, some)

        if issubclass(some, Marker):
            return visit_marker(ctx, some)

        if is_sized(some):
            if issubclass(some, Read):
                if issubclass(some, Write):
                    return visit_read_write_sized(ctx, some)

                return visit_read_sized(ctx, some)

    raise TypeError(f"{some!r} is not valid as type for fields.")


def create_field(ctx: Context, some: Type[Sized], offset: Optional[int] = None) -> Field[T]:
    if offset is None:
        offset = ctx.offset

    if is_class(some):
        if is_sized(some):
            if issubclass(some, Read):
                if issubclass(some, Write):
                    return MutField(cast(Type[ReadWriteSized[T]], some), offset)

                return Field(cast(Type[ReadSized[T]], some), offset)

    raise TypeError(f"Can not create field from {some!r}.")


def visit_struct(ctx: Context, marker_struct: Type[Struct]) -> Type[MemoryStruct]:
    fields: Dict[str, Field] = {}

    offset = ctx.offset

    size = 0

    annotations = getattr(marker_struct, ANNOTATIONS, {}).copy()

    for name, annotation in get_type_hints(marker_struct).items():
        try:
            field = create_field(ctx, visit_any(ctx, annotation))  # type: ignore

        except TypeError:
            continue

        if name in fields:
            raise ValueError(f"Repeated field: {name!r}.")

        annotations.pop(name)

        fields[name] = field

        field_size = field.size

        ctx.offset += field_size
        size += field_size

    ctx.offset = offset

    ctx.size += size

    @no_type_check
    class struct(  # type: ignore
        MemoryStruct, size=size, fields=fields, bits=ctx.bits, platform=ctx.platform
    ):
        vars().update(vars(marker_struct))

    setattr(struct, ANNOTATIONS, annotations)

    struct.__qualname__ = struct.__name__ = marker_struct.__name__

    for name, field in fields.items():
        if hasattr(struct, name):
            raise ValueError(f"Field attempts to overwrite name: {name!r}.")

        setattr(struct, name, field)

    return struct


def visit_union(ctx: Context, marker_union: Type[Union]) -> Type[MemoryUnion]:
    fields: Dict[str, Field] = {}

    size = 0

    annotations = getattr(marker_union, ANNOTATIONS, {}).copy()

    for name, annotation in get_type_hints(marker_union).items():
        try:
            field = create_field(ctx, visit_any(ctx, annotation))  # type: ignore

        except TypeError:
            continue

        if name in fields:
            raise ValueError(f"Repeated field: {name!r}.")

        annotations.pop(name)

        fields[name] = field

        field_size = field.size

        if field_size > size:
            size = field_size

    ctx.size += size

    @no_type_check
    class union(  # type: ignore
        MemoryUnion, size=size, fields=fields, bits=ctx.bits, platform=ctx.platform
    ):
        vars().update(vars(marker_union))

    setattr(union, ANNOTATIONS, annotations)

    union.__qualname__ = union.__name__ = marker_union.__name__

    for name, field in fields.items():
        if hasattr(union, name):
            raise ValueError(f"Field attempts to overwrite name: {name!r}.")

        setattr(union, name, field)

    return union


def visit_array(ctx: Context, marker_array: Type[Array]) -> Type[MemoryArray]:
    type = visit_any(ctx, marker_array.type)

    @no_type_check
    class array(  # type: ignore
        MemoryArray,
        type=type,
        length=marker_array.length,
        bits=ctx.bits,
        platform=ctx.platform,
    ):
        vars().update(vars(marker_array))

    array.__qualname__ = array.__name__ = marker_array.__name__

    return array


def visit_mut_array(ctx: Context, marker_mut_array: Type[MutArray]) -> Type[MemoryMutArray]:
    type = visit_any(ctx, marker_mut_array.type)

    @no_type_check
    class mut_array(  # type: ignore
        MemoryMutArray,
        type=type,
        length=marker_mut_array.length,
        bits=ctx.bits,
        platform=ctx.platform,
    ):
        vars().update(vars(marker_mut_array))

    mut_array.__qualname__ = mut_array.__name__ = marker_mut_array.__name__

    return mut_array


def visit_read_sized(ctx: Context, type: Type[ReadSized[T]]) -> Type[ReadSized[T]]:
    return type


def visit_read_write_sized(ctx: Context, type: Type[ReadWriteSized[T]]) -> Type[ReadWriteSized[T]]:
    return type


def visit_marker(ctx: Context, marker: Type[Marker]) -> Type[Sized]:
    return visit_any(ctx, ctx.get_type(marker.name))
