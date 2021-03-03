from gd.memory.context import Context
from gd.memory.export import is_export
from gd.memory.field import Field, MutField
from gd.memory.marker import (
    Marker,
    Array,
    MutArray,
    Pointer,
    MutPointer,
    Ref,
    MutRef,
    DynamicFill,
    Struct,
    Union,
    Void,
    fill,
    uintptr_t,
)
from gd.memory.memory_array import MemoryArray, MemoryMutArray
from gd.memory.memory_base import MemoryStruct, MemoryUnion
from gd.memory.memory_pointer_ref import MemoryPointer, MemoryMutPointer, MemoryRef, MemoryMutRef
from gd.memory.memory_void import MemoryVoid
from gd.memory.traits import Read, Write, Layout, ReadLayout, ReadWriteLayout, is_class, is_layout
from gd.platform import Platform, system_bits, system_platform
from gd.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
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
    from gd.memory.state import BaseState  # noqa

__all__ = ("Visitor",)

ANNOTATIONS = "__annotations__"
BASES = "__bases__"
MRO = "__mro__"

FINAL = "final"
PAD = "pad"
VTABLE = "vtable"

T = TypeVar("T")
V = TypeVar("V", bound="Visitor")


def pad_name(name: str) -> str:
    return f"__{PAD}_{name}__"


def vtable_name(name: str) -> str:
    return f"__{VTABLE}_{name}__"


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
    def create_field(self, some: Type[ReadWriteLayout[T]], offset: int) -> MutField[T]:  # noqa
        ...

    @overload  # noqa
    def create_field(self, some: Type[ReadLayout[T]], offset: int) -> Field[T]:  # noqa
        ...

    def create_field(self, some: Type[Any], offset: int = 0) -> Field[T]:  # noqa
        if is_class(some):
            if is_layout(some):
                if issubclass(some, Read):
                    if issubclass(some, Write):
                        mut_type = cast(Type[ReadWriteLayout[T]], some)

                        return MutField(mut_type, offset)

                    type = cast(Type[ReadLayout[T]], some)

                    return Field(type, offset)

        raise InvalidMemoryType(f"Can not create field from {some!r}.")

    def visit_any(self, some: Any) -> Type[Layout]:
        if is_class(some):
            if is_layout(some):
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

            if issubclass(some, DynamicFill):
                dynamic_fill = cast(Type[DynamicFill], some)

                return self.visit_dynamic_fill(dynamic_fill)

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

    def visit_dynamic_fill(self, dynamic_fill: Type[DynamicFill]) -> Type[Layout]:
        return self.visit_array(
            fill(dynamic_fill.fill.get((self.context.bits, self.context.platform), 0))
        )

    @classmethod
    def export_members(cls, export_class: Type[Any], import_class: Type[Any]) -> None:
        for base in getattr(export_class, MRO):
            for name, member in vars(base).items():
                if is_export(member):
                    setattr(import_class, name, member)

    # Maybe we could implement This (or this) type,
    # which is going to be used for recursive definitions.

    # XXX: improvement of subclassing is highly recommended.

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
            # XXX: we need to do something in case of ambiguity

            if getattr(base, VTABLE, None):
                if not any(
                    issubclass(other_base, Struct)
                    and other_base is not Struct
                    and other_base is not base
                    and issubclass(base, other_base)
                    for other_base in reversed(bases)
                ):
                    # XXX: it is not really base name, though
                    annotations[vtable_name(base.__name__)] = uintptr_t

            annotations.update(getattr(base, ANNOTATIONS, {}))

        # XXX: implement vtable optimization

        class annotation_holder:
            pass

        setattr(annotation_holder, ANNOTATIONS, annotations)

        # initialize variables used in fetching fields, size and offsets

        field_array: List[Tuple[str, Field]] = []

        alignment = 0

        # iterate through annotations and figure out all the fields

        for name, annotation in get_type_hints(annotation_holder).items():
            try:
                field: Field[Any] = self.create_field(self.visit_any(annotation))  # type: ignore

            except InvalidMemoryType:
                continue

            field_array.append((name, field))

            if field.alignment > alignment:
                alignment = field.alignment

        # if structure is not packed

        if not marker_struct.packed:

            # copy original fields in order to iterate properly

            original_fields = dict(field_array)

            index = 0

            for main_name, main_field in original_fields.items():
                temp_size = 0

                # calculate size of all fields preceding current field

                for _, field in field_array:
                    if field is main_field:
                        break

                    temp_size += field.size

                remain_size = temp_size % main_field.alignment

                # if size is not divisible by alignment of the field, pad accordingly

                if remain_size:
                    pad_size = main_field.alignment - remain_size

                    name = pad_name(main_name)

                    field_array.insert(
                        index,
                        (name, self.create_field(self.visit_array(fill(pad_size))))  # type: ignore
                    )

                    index += 1

                index += 1

            # update fields, setting their offsets and computing total size along

            fields: Dict[str, Field] = dict(field_array)

            offset = 0
            size = 0

            for field in fields.values():
                field.offset = offset

                offset += field.size
                size += field.size

                field.freeze()  # freeze the field so it can not be mutated

            # last padding: we need the structure size to be divisible
            # by the size of the largest member in it

            if alignment:
                remain_size = size % alignment

                if remain_size:
                    pad_size = alignment - remain_size

                    fields[pad_name(FINAL)] = self.create_field(
                        self.visit_array(fill(pad_size)), offset  # type: ignore
                    )

                    offset += pad_size
                    size += pad_size

        # create actual struct type

        @no_type_check
        class struct(  # type: ignore
            MemoryStruct,
            size=size,
            alignment=alignment,
            fields=fields,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        self.export_members(marker_struct, struct)

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

        alignment = 0
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
                field: Field[Any] = self.create_field(self.visit_any(annotation))  # type: ignore

            except InvalidMemoryType:
                continue

            fields[name] = field

            if field.size > size:
                size = field.size

            if field.alignment > alignment:
                alignment = field.alignment

        @no_type_check
        class union(  # type: ignore
            MemoryUnion,
            size=size,
            alignment=alignment,
            fields=fields,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        self.export_members(marker_union, union)

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
            pass

        self.export_members(marker_pointer, pointer)

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
            pass

        self.export_members(marker_mut_pointer, mut_pointer)

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
            pass

        self.export_members(marker_ref, ref)

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
            pass

        self.export_members(marker_mut_ref, mut_ref)

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
            pass

        self.export_members(marker_array, array)

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
            pass

        self.export_members(marker_mut_array, mut_array)

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

    def visit_read_sized(self, type: Type[ReadLayout[T]]) -> Type[ReadLayout[T]]:
        return type

    def visit_read_write_sized(self, type: Type[ReadWriteLayout[T]]) -> Type[ReadWriteLayout[T]]:
        return type

    def visit_marker(self, marker: Type[Marker]) -> Type[Layout]:
        return self.visit_any(self.context.get_type(marker.name))
