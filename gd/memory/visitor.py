from gd.memory.array import MemoryArray, MemoryMutArray
from gd.memory.base import MemoryStruct, MemoryUnion
from gd.memory.common_traits import ReadSized, ReadWriteSized
from gd.memory.context import Context
from gd.memory.field import Field, MutField
from gd.memory.marker import (
    Marker, Array, MutArray, Pointer, MutPointer, Ref, MutRef, Struct, Union
)
from gd.memory.pointer_ref import MemoryPointer, MemoryMutPointer, MemoryRef, MemoryMutRef
from gd.memory.traits import Read, Write, Sized, is_class, is_sized
from gd.platform import Platform, system_bits, system_platform
from gd.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Type,
    TypeVar,
    Union as TypeUnion,
    cast,
    get_type_hints,
    no_type_check,
    overload,
)

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("Visitor",)

ANNOTATIONS = "__annotations__"
NO_TYPE_CHECK = "__no_type_check__"

T = TypeVar("T")
V = TypeVar("V", bound="Visitor")


class InvalidMemoryType(TypeError):
    pass


class Visitor:
    def __init__(self, context: Context) -> None:
        self._context = context

    @classmethod
    def with_context(
        cls: Type[V],
        bits: int = system_bits,
        platform: TypeUnion[int, str, Platform] = system_platform,
    ) -> V:
        return cls(Context(bits, platform))  # type: ignore

    @classmethod
    def bound(cls: Type[V], state: "BaseState") -> V:
        return cls(Context.bound(state))  # type: ignore

    @property
    def context(self) -> Context:
        return self._context

    @overload  # noqa
    def create_field(self, some: Type[ReadWriteSized[T]], offset: int) -> MutField[T]:  # noqa
        ...

    @overload  # noqa
    def create_field(self, some: Type[ReadSized[T]], offset: int) -> Field[T]:  # noqa
        ...

    def create_field(self, some: Type[Any], offset: int = 0) -> Field[T]:  # noqa
        if is_class(some):
            if is_sized(some):
                if issubclass(some, Read):
                    if issubclass(some, Write):
                        mut_type = cast(Type[ReadWriteSized[T]], some)

                        return MutField(mut_type, offset)

                    type = cast(Type[ReadSized[T]], some)

                    return Field(type, offset)

        raise InvalidMemoryType(f"Can not create field from {some!r}.")

    def visit_any(self, some: Any) -> Type[Sized]:
        if is_class(some):
            if issubclass(some, Struct):
                struct = cast(Type[Struct], some)

                return self.visit_struct(struct)

            if issubclass(some, Union):
                union = cast(Type[Union], some)

                return self.visit_union(union)

            if issubclass(some, Ref):
                if issubclass(some, MutRef):
                    return self.visit_mut_ref(some)

                return self.visit_ref(some)

            if issubclass(some, Pointer):
                if issubclass(some, MutPointer):
                    return self.visit_mut_pointer(some)

                return self.visit_pointer(some)

            if issubclass(some, Array):
                if issubclass(some, MutArray):
                    return self.visit_mut_array(some)

                return self.visit_array(some)

            if issubclass(some, Marker):
                return self.visit_marker(some)

            if is_sized(some):
                if issubclass(some, Read):
                    if issubclass(some, Write):
                        return self.visit_read_write_sized(some)

                    return self.visit_read_sized(some)

        raise InvalidMemoryType(f"{some!r} is not valid as memory type.")

    def get_type_for_hints(self, type: Type[Any]) -> Type[Any]:
        if getattr(type, NO_TYPE_CHECK, None):
            class hint_type:
                pass

            hint_type.__qualname__ = hint_type.__name__ = type.__name__

            return hint_type

        return type

    # Things we should implement are listed below:

    # offset(...) -> Offset(...) for dynamic offsets in relation to platforms and their bitness.
    # For example, _offset: offset(windows_x32=4, windows_x64=8)
    # is somewhat similar to _offset: uintptr_t.

    # Perhaps Base, which Struct and Union inherit from, should have compute_offset function,
    # which can be used to compute initial offset, having default version of:

    # @staticmethod
    # def compute_offset(ctx: Context) -> int:
    #     return 0

    # It can be used for weird structures like std::string in libstdc++

    # class std_long_string(Struct):
    #     capacity: uintsize_t
    #     length: uintsize_t
    #     refcount: int_t
    #     content: mut_array(char_t)  # <- this will fail, by the way

    #     @staticmethod
    #     def compute_offset(ctx: Context) -> int:
    #         types = ctx.types
    #         size = types.int_t.size + types.uintsize_t.size * 2
    #         return -size

    # With such function, content will have offset of 0, which is exactly what we need.

    # Then we can have the following:

    # class std_string(Struct):
    #     pointer: mut_pointer(std_long_string)

    # And our std_string is going to be approximately the same as std::string.

    # Maybe we could also implement This (or this) type, which would be used
    # as some way for fields to reference the structure or union they are in.

    def visit_struct(self, marker_struct: Type[Struct]) -> Type[MemoryStruct]:
        fields: Dict[str, Field] = {}

        annotations = getattr(marker_struct, ANNOTATIONS, {}).copy()

        offset = 0
        size = 0

        for name, annotation in get_type_hints(
            self.get_type_for_hints(marker_struct)
        ).items():
            try:
                field: Field[Any] = self.create_field(
                    self.visit_any(annotation), offset  # type: ignore
                )

            except InvalidMemoryType:
                continue

            if name in fields:
                raise ValueError(f"Repeated field: {name!r}.")

            annotations[name] = field.type

            fields[name] = field

            offset += field.size
            size += field.size

        @no_type_check
        class struct(  # type: ignore
            MemoryStruct,
            size=size,
            fields=fields,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_struct))

        setattr(struct, ANNOTATIONS, annotations)

        struct.__qualname__ = struct.__name__ = marker_struct.__name__

        for name, field in fields.items():
            if hasattr(struct, name):
                raise ValueError(f"Field attempts to overwrite name: {name!r}.")

            setattr(struct, name, field)

        return struct

    def visit_union(self, marker_union: Type[Union]) -> Type[MemoryUnion]:
        fields: Dict[str, Field] = {}

        offset = 0
        size = 0

        annotations = getattr(marker_union, ANNOTATIONS, {}).copy()

        for name, annotation in get_type_hints(
            self.get_type_for_hints(marker_union)
        ).items():
            try:
                field: Field[Any] = self.create_field(
                    self.visit_any(annotation), offset  # type: ignore
                )

            except InvalidMemoryType:
                continue

            if name in fields:
                raise ValueError(f"Repeated field: {name!r}.")

            annotations[name] = field.type

            fields[name] = field

            if field.size > size:
                size = field.size

        @no_type_check
        class union(  # type: ignore
            MemoryUnion,
            size=size,
            fields=fields,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_union))

        setattr(union, ANNOTATIONS, annotations)

        union.__qualname__ = union.__name__ = marker_union.__name__

        for name, field in fields.items():
            if hasattr(union, name):
                raise ValueError(f"Field attempts to overwrite name: {name!r}.")

            setattr(union, name, field)

        return union

    def visit_pointer(self, marker_pointer: Type[Pointer]) -> Type[MemoryPointer[T]]:
        type = self.visit_any(marker_pointer.type)

        types = self.context.types

        pointer_type = types.intptr_t if marker_pointer.signed else types.uintptr_t  # type: ignore

        @no_type_check
        class pointer(  # type: ignore
            MemoryPointer,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_pointer))

        pointer.__qualname__ = pointer.__name__ = marker_pointer.__name__

        return pointer

    def visit_mut_pointer(self, marker_mut_pointer: Type[MutPointer]) -> Type[MemoryMutPointer[T]]:
        type = self.visit_any(marker_mut_pointer.type)

        types = self.context.types

        pointer_type = (
            types.intptr_t if marker_mut_pointer.signed else types.uintptr_t  # type: ignore
        )

        @no_type_check
        class mut_pointer(  # type: ignore
            MemoryMutPointer,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_mut_pointer))

        mut_pointer.__qualname__ = mut_pointer.__name__ = marker_mut_pointer.__name__

        return mut_pointer

    def visit_ref(self, marker_ref: Type[Ref]) -> Type[MemoryRef[T]]:
        type = self.visit_any(marker_ref.type)

        types = self.context.types

        pointer_type = types.intptr_t if marker_ref.signed else types.uintptr_t  # type: ignore

        @no_type_check
        class ref(  # type: ignore
            MemoryRef,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_ref))

        ref.__qualname__ = ref.__name__ = marker_ref.__name__

        return ref

    def visit_mut_ref(self, marker_mut_ref: Type[MutRef]) -> Type[MemoryMutRef[T]]:
        type = self.visit_any(marker_mut_ref.type)

        types = self.context.types

        pointer_type = (
            types.intptr_t if marker_mut_ref.signed else types.uintptr_t  # type: ignore
        )

        @no_type_check
        class mut_ref(  # type: ignore
            MemoryMutRef,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_mut_ref))

        mut_ref.__qualname__ = mut_ref.__name__ = marker_mut_ref.__name__

        return mut_ref

    def visit_array(self, marker_array: Type[Array]) -> Type[MemoryArray[T]]:
        type = self.visit_any(marker_array.type)

        @no_type_check
        class array(  # type: ignore
            MemoryArray,
            type=type,
            length=marker_array.length,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_array))

        array.__qualname__ = array.__name__ = marker_array.__name__

        return array

    def visit_mut_array(self, marker_mut_array: Type[MutArray]) -> Type[MemoryMutArray[T]]:
        type = self.visit_any(marker_mut_array.type)

        @no_type_check
        class mut_array(  # type: ignore
            MemoryMutArray,
            type=type,
            length=marker_mut_array.length,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            vars().update(vars(marker_mut_array))

        mut_array.__qualname__ = mut_array.__name__ = marker_mut_array.__name__

        return mut_array

    def visit_read_sized(self, type: Type[ReadSized[T]]) -> Type[ReadSized[T]]:
        return type

    def visit_read_write_sized(self, type: Type[ReadWriteSized[T]]) -> Type[ReadWriteSized[T]]:
        return type

    def visit_marker(self, marker: Type[Marker]) -> Type[Sized]:
        return self.visit_any(self.context.get_type(marker.name))
