from abc import abstractmethod
from functools import wraps
from typing import Type, TypeVar

from attrs import define
from typing_extensions import Protocol, runtime_checkable

from gd.memory.context import Context
from gd.memory.field import Field, MutField
from gd.memory.markers import (
    Array,
    DynamicFill,
    MutArray,
    MutPointer,
    MutRef,
    Pointer,
    Ref,
    SimpleMarker,
    Struct,
    This,
    Union,
    Void,
    fill,
    uintptr_t,
)
from gd.memory.memory import Memory
from gd.memory.memory_arrays import MemoryArray, MemoryMutArray
from gd.memory.memory_base import MemoryStruct, MemoryUnion
from gd.memory.memory_pointers_refs import (
    MemoryMutPointer,
    MemoryMutRef,
    MemoryPointer,
    MemoryRef,
)
from gd.memory.memory_special import MemoryThis, MemoryVoid
from gd.memory.state import AbstractState
from gd.memory.traits import Layout, Read, ReadWrite, Write, is_layout
from gd.memory.utils import set_name
from gd.platform import SYSTEM_PLATFORM_CONFIG, PlatformConfig
from gd.typing import Binary, Namespace, get_name

__all__ = ("Visitable", "AnyVisitable", "Visitor")


VS = TypeVar("VS", bound="Visitor", contravariant=True)


@runtime_checkable
class Visitable(Protocol[VS]):
    @classmethod
    @abstractmethod
    def accept(cls, visitor: VS) -> Type[Layout]:
        ...


ANNOTATIONS = "__annotations__"
BASES = "__bases__"
MRO = "__mro__"

FINAL = "final"
PAD = "pad"
VTABLE = "vtable"

MERGED_METACLASS = "merged_metaclass"
STRUCT_TYPE = "struct_type"
UNION_TYPE = "union_type"
ARRAY_TYPE = "array_type"
MUT_ARRAY_TYPE = "mut_array_type"
POINTER_TYPE = "pointer_type"
MUT_POINTER_TYPE = "mut_pointer_type"
REF_TYPE = "ref_type"
MUT_REF_TYPE = "mut_ref_type"
THIS_TYPE = "this_type"
VOID_TYPE = "void_type"

T = TypeVar("T")

PAD_NAME = "__{}_{}__"


def pad_name(name: str) -> str:
    return PAD_NAME.format(PAD, name)


def vtable_name(name: str) -> str:
    return PAD_NAME.format(VTABLE, name)


class InvalidMemoryType(TypeError):
    pass


VISITOR_CACHE: Namespace = {}
VISITOR_CACHE_KEY = "{}@{:x}[{}]"


V = TypeVar("V", bound="Visitor")


def visitor_cache(visit: Binary[V, Visitable[V], T]) -> Binary[V, Visitable[V], T]:
    @wraps(visit)
    def visit_function(visitor: V, some: Visitable[V]) -> T:
        visitor_cache_key = VISITOR_CACHE_KEY.format(
            get_name(type(some)),
            id(some),
            visitor.config,
        )

        if visitor_cache_key not in VISITOR_CACHE:
            VISITOR_CACHE[visitor_cache_key] = visit(visitor, some)

        return VISITOR_CACHE[visitor_cache_key]

    return visit_function


@define()
class Visitor:
    context: Context

    @property
    def config(self) -> PlatformConfig:
        return self.context.config

    @classmethod
    def bound(cls: Type[V], state: AbstractState) -> V:
        return cls(Context.bound(state))

    def create_field(self, some: Type[Read[T]]) -> Field[T]:
        return Field(some)

    def create_mut_field(self, some: Type[ReadWrite[T]]) -> MutField[T]:
        return MutField(some)

    @visitor_cache
    def visit(self: V, visitable: Visitable[V]) -> Type[Layout]:
        return visitable.accept(self)

    def visit_dynamic_fill(self, dynamic_fill: Type[DynamicFill]) -> Type[MemoryArray]:
        return self.visit_array(fill(dynamic_fill.fills.get(self.config, 0)))

    def visit_struct(self, marker_struct: Type[Struct]) -> Type[MemoryStruct]:
        # get all bases via resolving the MRO

        bases = marker_struct.mro()

        # get direct (main) base

        direct_base, *_ = bases

        # if struct has inherited annotations, and does not define any on its own, reset

        if getattr(marker_struct, ANNOTATIONS, {}) == getattr(direct_base, ANNOTATIONS, {}):
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
                # if the field has null alignment, move onto the next one

                if not main_field.alignment:
                    continue

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
                        (name, self.create_field(self.visit_array(fill(pad_size)))),  # type: ignore
                    )

                    index += 1

                index += 1

            # update fields, setting their offsets and computing total size along

            fields: Dict[str, Field] = dict(field_array)

            size = 0

            if fields:
                origin = marker_struct.origin

                actual_fields = list(fields.values())

                before_origin, after_origin = actual_fields[:origin], actual_fields[origin:]

                # go through fields before the origin

                offset = 0

                for field in reversed(before_origin):
                    try:
                        offset -= field.size
                        size += field.size

                    except TypeError:
                        pass

                    field.offset = offset

                    field.freeze()  # freeze the field so it can not be mutated

                # now to process the origin and everything after it

                offset = 0

                for field in after_origin:
                    field.offset = offset

                    try:
                        offset += field.size
                        size += field.size

                    except TypeError:
                        pass

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
            # merge marker struct with memory struct
            marker_struct,  # type: ignore
            MemoryStruct,
            metaclass=merge_metaclass(  # type: ignore
                MemoryStruct, marker_struct, name=STRUCT_TYPE
            ),
            # set derive to false
            derive=False,
            # other arguments
            size=size,
            alignment=alignment,
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

        self.resolve_recursion(fields, struct)

        return struct

    def resolve_recursion(self, fields: Dict[str, Field], this: Type[MemoryBase]) -> None:
        for field in fields.values():
            self.resolve_recursion_type(field.type, this)

    def resolve_recursion_type(
        self, type: Type[Layout], this: Type[MemoryBase], in_pointer: bool = False
    ) -> None:
        if issubclass(type, MemoryThis):
            # reaching here implies we are directly having this -> infinite size

            raise TypeError("Infinite size detected while recursively resolving this.")

        if issubclass(type, MemoryBaseArray):
            self.resolve_recursion_array(type, this, in_pointer=in_pointer)

        if issubclass(type, MemoryBasePointer):
            self.resolve_recursion_pointer(type, this)

        # we do not really care about anything else

    def resolve_recursion_array(
        self, array: Type[MemoryBaseArray], this: Type[MemoryBase], in_pointer: bool
    ) -> None:
        if issubclass(array.type, MemoryThis):
            if in_pointer:
                array._type = this  # perhaps there might be some better way?

        self.resolve_recursion_type(array.type, this, in_pointer=in_pointer)  # pass in_pointer

    def resolve_recursion_pointer(
        self, pointer: Type[MemoryBasePointer], this: Type[MemoryBase]
    ) -> None:
        if issubclass(pointer.type, MemoryThis):
            pointer._type = this  # there might be some better way, I suppose

        self.resolve_recursion_type(pointer.type, this, in_pointer=True)  # in_pointer -> true

    def visit_union(self, marker_union: Type[Union]) -> Type[MemoryUnion]:
        # initialize variables needed to get fields and size

        fields: Dict[str, Field] = {}

        alignment = 0
        size = 0

        # acquire all annotations

        annotations = {}

        for base in marker_union.mro():
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
            # merge marker union with memory union
            marker_union,  # type: ignore
            MemoryUnion,
            metaclass=merge_metaclass(MemoryUnion, marker_union, name=UNION_TYPE),  # type: ignore
            # set derive to false
            derive=False,
            # other arguments
            size=size,
            alignment=alignment,
            fields=fields,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        union.__qualname__ = union.__name__ = marker_union.__name__

        for name, field in fields.items():
            if hasattr(union, name):
                raise ValueError(f"Field attempts to overwrite name: {name!r}.")

            setattr(union, name, field)

        self.resolve_recursion(fields, union)

        return union

    def visit_pointer(self, marker_pointer: Type[Pointer]) -> Type[MemoryPointer[T]]:
        type = self.visit_any(marker_pointer.type)

        types = self.context.types

        pointer_type = types.intptr_t if marker_pointer.signed else types.uintptr_t  # type: ignore

        @no_type_check
        class pointer(  # type: ignore
            # merge marker pointer with memory pointer
            MemoryPointer,
            marker_pointer,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryPointer, marker_pointer, name=POINTER_TYPE
            ),
            # set derive to false
            derive=False,
            # other arguments
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
            # merge marker mutable pointer with memory mutable pointer
            MemoryMutPointer,
            marker_mut_pointer,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryMutPointer, marker_mut_pointer, name=MUT_POINTER_TYPE
            ),
            # set derive to false
            derive=False,
            # other arguments
            type=type,
            pointer_type=pointer_type,
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        mut_pointer.__qualname__ = mut_pointer.__name__ = marker_mut_pointer.__name__

        return mut_pointer

    def visit_ref(self, marker_ref: Type[Ref]) -> Type[MemoryRef[T]]:
        class ref(
            MemoryRef,
            type=self.visit(marker_ref.type),
            pointer_type=self.visit_simple(uintptr_t),
            config=self.config,
        ):
            pass

        set_name(ref, get_name(marker_ref))

        return ref

    def visit_mut_ref(self, marker_mut_ref: Type[MutRef]) -> Type[MemoryMutRef[T]]:
        class mut_ref(
            MemoryMutRef,
            type=self.visit(marker_mut_ref.type),
            pointer_type=self.visit_simple(uintptr_t),
            config=self.config,
        ):
            pass

        set_name(mut_ref, get_name(marker_mut_ref))

        return mut_ref

    def visit_array(self, marker_array: Type[Array]) -> Type[MemoryArray[T]]:
        class array(
            MemoryArray,
            type=self.visit(marker_array.type),
            length=marker_array.length,
            config=self.config,
        ):
            pass

        set_name(array, get_name(marker_array))

        return array

    def visit_mut_array(self, marker_mut_array: Type[MutArray]) -> Type[MemoryMutArray[T]]:
        class mut_array(
            MemoryMutArray,
            type=self.visit(marker_mut_array.type),
            length=marker_mut_array.length,
            config=self.config,
        ):
            pass

        set_name(mut_array, get_name(marker_mut_array))

        return mut_array

    def visit_void(self, marker_void: Type[Void]) -> Type[MemoryVoid]:
        class void(MemoryVoid, config=self.config):
            pass

        set_name(void, get_name(marker_void))

        return void

    def visit_this(self, marker_this: Type[This]) -> Type[MemoryThis]:
        class this(MemoryThis, config=self.config):
            pass

        set_name(this, get_name(marker_this))

        return this

    def visit_simple(self, marker: Type[SimpleMarker]) -> Type[Memory]:
        return self.visit(self.context.get(marker.name))


AnyVisitable = Visitable[Visitor]
