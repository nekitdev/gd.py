# DOCUMENT + FINISH

from abc import abstractmethod
from functools import wraps

from attrs import define
from typing_extensions import Protocol, runtime_checkable

from gd.memory.context import Context
from gd.memory.field import Field, MutField
from gd.memory.marker import (
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
from gd.memory.memory_array import MemoryArray, MemoryBaseArray, MemoryMutArray
from gd.memory.memory_base import MemoryBase, MemoryStruct, MemoryUnion
from gd.memory.memory_pointer_ref import (
    MemoryBasePointer,
    MemoryMutPointer,
    MemoryMutRef,
    MemoryPointer,
    MemoryRef,
)
from gd.memory.memory_special import MemoryThis, MemoryVoid
from gd.memory.state import AbstractState
from gd.memory.traits import Layout, Read, ReadLayout, ReadWriteLayout, Write, is_class, is_layout
from gd.platform import Platform, platform_to_string, system_bits, system_platform
from gd.typing import TYPE_CHECKING, Any, Binary, Callable, Dict, List, Named, Tuple, Type, TypeVar, get_name
from gd.typing import Union as TypeUnion
from gd.typing import cast, get_type_hints, no_type_check, overload

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("Visitor",)


VS = TypeVar("VS", bound="Visitor", contravariant=True)


@runtime_checkable
class Visitable(Protocol[VS]):
    @abstractmethod
    def accept(self, visitor: VS) -> Type[Layout]:
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


VISITOR_CACHE: Dict[str, Any] = {}
VISITOR_CACHE_KEY = "{}@{:x}[{}]"


V = TypeVar("V", bound="Visitor")


def visitor_cache(visit: Binary[V, Visitable[V], T]) -> Binary[V, Visitable[V], T]:
    @wraps(visit)
    def visit_function(visitor: V, some: Visitable[V]) -> T:
        visitor_cache_key = VISITOR_CACHE_KEY.format(
            get_name(some),
            id(some),
            visitor.context.config,
        )

        if visitor_cache_key not in VISITOR_CACHE:
            VISITOR_CACHE[visitor_cache_key] = visit(visitor, some)

        return VISITOR_CACHE[visitor_cache_key]

    return visit_function


@define()
class Visitor:
    context: Context

    @classmethod
    def bound(cls: Type[V], state: AbstractState) -> V:
        return cls(Context.bound(state))

    def create_field(self, some: Type[Read[T]]) -> Field[T]:
        ...

    def create_mut_field(self, some: Type[ReadWrite[T]]) -> MutField[T]:
        ...

    @visitor_cache
    def visit(self: V, visitable: Visitable[V]) -> Type[Layout]:
        return visitable.accept(self)

    def visit_dynamic_fill(self, dynamic_fill: Type[DynamicFill]) -> Type[Layout]:
        return self.visit_array(fill(dynamic_fill.fill.get(self.context.config, 0)))

    def visit_struct(self, marker_struct: Type[Struct]) -> Type[MemoryStruct]:
        # get all bases via resolving the MRO

        bases = getattr(marker_struct, MRO)

        # get direct (main) base

        direct_bases = getattr(marker_struct, BASES)

        direct_base, *_ = direct_bases

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
        type = self.visit_any(marker_ref.type)

        types = self.context.types

        pointer_type = types.intptr_t if marker_ref.signed else types.uintptr_t  # type: ignore

        @no_type_check
        class ref(  # type: ignore
            # merge marker reference with memory reference
            MemoryRef,
            marker_ref,  # type: ignore
            metaclass=merge_metaclass(MemoryRef, marker_ref, name=REF_TYPE),  # type: ignore
            # set derive to false
            derive=False,
            # other arguments
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

        pointer_type = types.intptr_t if marker_mut_ref.signed else types.uintptr_t  # type: ignore

        @no_type_check
        class mut_ref(  # type: ignore
            # merge marker mutable reference with memory mutable reference
            MemoryMutRef,
            marker_mut_ref,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryMutRef, marker_mut_ref, name=MUT_REF_TYPE
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

        mut_ref.__qualname__ = mut_ref.__name__ = marker_mut_ref.__name__

        return mut_ref

    def visit_array(self, marker_array: Type[Array]) -> Type[MemoryArray[T]]:
        type = self.visit_any(marker_array.type)

        @no_type_check
        class array(  # type: ignore
            # merge marker array with memory array
            MemoryArray,
            marker_array,  # type: ignore
            metaclass=merge_metaclass(MemoryArray, marker_array, name=ARRAY_TYPE),  # type: ignore
            # set derive to false
            derive=False,
            # other arguments
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
            # merge marker mutable array with memory mutable array
            MemoryMutArray,
            marker_mut_array,  # type: ignore
            metaclass=merge_metaclass(  # type: ignore
                MemoryMutArray, marker_mut_array, name=MUT_ARRAY_TYPE
            ),
            # set derive to false
            derive=False,
            # other arguments
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
            # merge marker void with memory void
            MemoryVoid,
            marker_void,  # type: ignore
            metaclass=merge_metaclass(MemoryVoid, marker_void, name=VOID_TYPE),  # type: ignore
            # set derive to false, and special to true
            derive=False,
            special=True,
            # other arguments
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        void.__qualname__ = void.__name__ = marker_void.__name__

        return void

    def visit_this(self, marker_this: Type[Void]) -> Type[MemoryThis]:
        @no_type_check
        class this(  # type: ignore
            # merge marker this with memory this
            MemoryThis,
            marker_this,  # type: ignore
            metaclass=merge_metaclass(MemoryThis, marker_this, name=THIS_TYPE),  # type: ignore
            # set derive to false, and special to true
            derive=False,
            special=True,
            # other arguments
            bits=self.context.bits,
            platform=self.context.platform,
        ):
            pass

        this.__qualname__ = this.__name__ = marker_this.__name__

        return this

    def visit_read_sized(self, type: Type[ReadLayout[T]]) -> Type[ReadLayout[T]]:
        return type

    def visit_read_write_sized(self, type: Type[ReadWriteLayout[T]]) -> Type[ReadWriteLayout[T]]:
        return type

    def visit_simple_marker(self, marker: Type[SimpleMarker]) -> Type[Layout]:
        return self.visit(self.context.get(marker.name))


AnyVisitable = Visitable[Visitor]
