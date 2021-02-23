from gd.memory.array import MemoryArray, MemoryMutArray
from gd.memory.base import MemoryStruct, MemoryUnion
from gd.memory.common_traits import ReadSized, ReadWriteSized
from gd.memory.context import Context
from gd.memory.field import Field, MutField
from gd.memory.marker import (
    Marker,
    Array,
    MutArray,
    Pointer,
    MutPointer,
    Ref,
    MutRef,
    Fill,
    Struct,
    Union,
    Void,
    array,
    char_t,
    uintptr_t,
)
from gd.memory.pointer_ref import MemoryPointer, MemoryMutPointer, MemoryRef, MemoryMutRef
from gd.memory.traits import Read, Write, Sized, is_class, is_sized
from gd.memory.void import MemoryVoid
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
BASES = "__bases__"
MRO = "__mro__"

MERGED_METACLASS = "merged_metaclass"

ARRAY_TYPE = "array_type"
MUT_ARRAY_TYPE = "mut_array_type"
POINTER_TYPE = "pointer_type"
MUT_POINTER_TYPE = "mut_pointer_type"
REF_TYPE = "ref_type"
MUT_REF_TYPE = "mut_ref_type"
STRUCT_TYPE = "struct_type"
UNION_TYPE = "union_type"

VTABLE = "vtable"

T = TypeVar("T")
V = TypeVar("V", bound="Visitor")


def vtable_name(name: str) -> str:
    return f"__{VTABLE}_{name}__"


@no_type_check
def merge_metaclass(*types: Type[Any], name: str = MERGED_METACLASS) -> Type[Type[Any]]:
    class merged_metaclass(*map(type, types)):
        pass

    merged_metaclass.__qualname__ = merged_metaclass.__name__ = name

    return merged_metaclass


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
            if is_sized(some):
                if issubclass(some, Read):
                    if issubclass(some, Write):
                        return self.visit_read_write_sized(some)

                    return self.visit_read_sized(some)

            if issubclass(some, Struct):
                struct = cast(Type[Struct], some)

                return self.visit_struct(struct)

            if issubclass(some, Union):
                union = cast(Type[Union], some)

                return self.visit_union(union)

            if issubclass(some, Void):
                return self.visit_void(some)

            if issubclass(some, Fill):
                fill = cast(Type[Fill], some)

                return self.visit_fill(fill)

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

        raise InvalidMemoryType(f"{some!r} is not valid as memory type.")

    def visit_fill(self, fill: Type[Fill]) -> Type[Sized]:
        length = fill.fill.get((self.context.bits, self.context.platform), 0)

        return self.visit_array(array(char_t, length))

    # Things we should implement are listed below:

    # Maybe we could implement This (or this) type,
    # which is going to be used for recursive definitions.

    # We do not yet have vtable optimization, and this will cause invalid layouts
    # when we are going to deal with complex virtual inheritance, so this needs to be fixed.

    # Just like with vtables, we do not have padding implemented, which is going to result
    # in invalid layouts.

    def visit_struct(self, marker_struct: Type[Struct]) -> Type[MemoryStruct]:
        # get all bases via resolving the MRO

        bases = getattr(marker_struct, MRO)

        # if struct has inherited annotations, and does not define any on its own, reset

        _, main_base, *_ = bases

        if getattr(marker_struct, ANNOTATIONS, {}) == getattr(main_base, ANNOTATIONS, {}):
            setattr(marker_struct, ANNOTATIONS, {})

        # fetch annotations

        annotations = {}

        for base in reversed(bases):
            # account for vtables

            if getattr(base, VTABLE, None):
                annotations[vtable_name(base.__name__)] = uintptr_t

            annotations.update(getattr(base, ANNOTATIONS, {}))

        # XXX: implement vtable optimization

        class annotation_holder:
            pass

        setattr(annotation_holder, ANNOTATIONS, annotations)

        # initialize variables used in fetching fields, size and offsets

        fields: Dict[str, Field] = {}

        offset = 0

        max_size = 0
        size = 0

        # iterate through annotations and figure out all the fields

        for name, annotation in get_type_hints(annotation_holder).items():
            try:
                field: Field[Any] = self.create_field(
                    self.visit_any(annotation), offset  # type: ignore
                )

            except InvalidMemoryType:
                continue

            fields[name] = field

            if field.size > max_size:
                max_size = field.size

            offset += field.size
            size += field.size

        # create actual struct type

        @no_type_check
        class struct(  # type: ignore
            MemoryStruct,
            marker_struct,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryStruct, marker_struct, name=STRUCT_TYPE
            ),
            derive=False,
            size=size,
            fields=fields,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        # fix struct name

        struct.__qualname__ = struct.__name__ = marker_struct.__name__

        # attach fields

        for name, field in fields.items():
            if hasattr(struct, name):
                raise ValueError(f"Field attempts to overwrite name: {name!r}.")

            setattr(struct, name, field)

        return struct

    def visit_union(self, marker_union: Type[Union]) -> Type[MemoryUnion]:
        # initialize variables needed to get fields and size

        fields: Dict[str, Field] = {}

        offset = 0
        size = 0

        # acquire all annotations

        annotations = {}

        for base in getattr(marker_union, MRO):
            annotations.update(getattr(base, ANNOTATIONS, {}))

        class annotation_holder:
            pass

        setattr(annotation_holder, ANNOTATIONS, annotations)

        # iterate through annotations

        for name, annotation in get_type_hints(annotation_holder).items():
            try:
                field: Field[Any] = self.create_field(
                    self.visit_any(annotation), offset  # type: ignore
                )

            except InvalidMemoryType:
                continue

            fields[name] = field

            if field.size > size:
                size = field.size

        @no_type_check
        class union(  # type: ignore
            MemoryUnion,
            marker_union,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryUnion, marker_union, name=UNION_TYPE
            ),
            derive=False,
            size=size,
            fields=fields,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

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
            marker_pointer,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryPointer, marker_pointer, name=POINTER_TYPE
            ),
            derive=False,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

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
            marker_mut_pointer,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryMutPointer, marker_mut_pointer, name=MUT_POINTER_TYPE
            ),
            derive=False,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        mut_pointer.__qualname__ = mut_pointer.__name__ = marker_mut_pointer.__name__

        return mut_pointer

    def visit_ref(self, marker_ref: Type[Ref]) -> Type[MemoryRef[T]]:
        type = self.visit_any(marker_ref.type)

        types = self.context.types

        pointer_type = types.intptr_t if marker_ref.signed else types.uintptr_t  # type: ignore

        @no_type_check
        class ref(  # type: ignore
            MemoryRef,
            marker_ref,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryRef, marker_ref, name=REF_TYPE
            ),
            derive=False,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

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
            marker_mut_ref,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryMutRef, marker_mut_ref, name=MUT_REF_TYPE
            ),
            derive=False,
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        mut_ref.__qualname__ = mut_ref.__name__ = marker_mut_ref.__name__

        return mut_ref

    def visit_array(self, marker_array: Type[Array]) -> Type[MemoryArray[T]]:
        type = self.visit_any(marker_array.type)

        @no_type_check
        class array(  # type: ignore
            MemoryArray,
            marker_array,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryArray, marker_array, name=ARRAY_TYPE
            ),
            derive=False,
            type=type,
            length=marker_array.length,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        array.__qualname__ = array.__name__ = marker_array.__name__

        return array

    def visit_mut_array(self, marker_mut_array: Type[MutArray]) -> Type[MemoryMutArray[T]]:
        type = self.visit_any(marker_mut_array.type)

        @no_type_check
        class mut_array(  # type: ignore
            MemoryMutArray,
            marker_mut_array,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryMutArray, marker_mut_array, name=MUT_ARRAY_TYPE
            ),
            derive=False,
            type=type,
            length=marker_mut_array.length,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        mut_array.__qualname__ = mut_array.__name__ = marker_mut_array.__name__

        return mut_array

    def visit_void(self, marker_void: Type[Void]) -> Type[MemoryVoid]:
        @no_type_check
        class void(  # type: ignore
            MemoryVoid, _root=True, bits=self.context.bits, platform=self.context.platform
        ):
            pass

        void.__qualname__ = void.__name__ = marker_void.__name__

        return void

    def visit_read_sized(self, type: Type[ReadSized[T]]) -> Type[ReadSized[T]]:
        return type

    def visit_read_write_sized(self, type: Type[ReadWriteSized[T]]) -> Type[ReadWriteSized[T]]:
        return type

    def visit_marker(self, marker: Type[Marker]) -> Type[Sized]:
        return self.visit_any(self.context.get_type(marker.name))
