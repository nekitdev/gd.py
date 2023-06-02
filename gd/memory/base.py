from __future__ import annotations

from builtins import setattr as set_attribute
from typing import TYPE_CHECKING, ClassVar, Type, TypeVar

from attrs import define, field, frozen
from funcs.decorators import cache
from named import get_module, get_name, set_module, set_name
from typing_extensions import final

from gd.enums import ByteOrder
from gd.memory.constants import DEFAULT_ALIGNMENT, DEFAULT_PACKED, DEFAULT_SIZE, DEFAULT_VIRTUAL
from gd.memory.data import Data
from gd.platform import SYSTEM_PLATFORM_CONFIG, PlatformConfig

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = ("Base", "Struct", "Union", "struct", "union")


@define()
class Base:
    ALIGNMENT: ClassVar[int] = DEFAULT_ALIGNMENT
    SIZE: ClassVar[int] = DEFAULT_SIZE

    state: AbstractState = field()
    address: int = field(repr=hex)
    order: ByteOrder = field(default=ByteOrder.NATIVE)


TS = TypeVar("TS", bound="Type[Struct]")


@define()
class Struct(Base):
    """Represents `struct` types."""

    PACKED: ClassVar[bool] = DEFAULT_PACKED
    VIRTUAL: ClassVar[bool] = DEFAULT_VIRTUAL

    @classmethod
    @cache
    def reconstruct(cls: TS, config: PlatformConfig) -> TS:
        return struct(cls.PACKED, cls.VIRTUAL, config)(cls)

    @classmethod
    def reconstruct_for(cls: TS, state: AbstractState) -> TS:
        return cls.reconstruct(state.config)


TU = TypeVar("TU", bound="Type[Union]")


@define()
class Union(Base):
    """Represents `union` types."""

    @classmethod
    @cache
    def reconstruct(cls: TU, config: PlatformConfig) -> TU:
        return union(config)(cls)

    @classmethod
    def reconstruct_for(cls: TU, state: AbstractState) -> TU:
        return cls.reconstruct(state.config)


S = TypeVar("S", bound=Struct)


@frozen()
class StructData(Data[S]):
    struct_type: Type[S] = field()

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> S:
        return self.compute_type(state.config)(state, address, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: S,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.compute_type(config).SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.compute_type(config).ALIGNMENT

    def compute_type(self, config: PlatformConfig) -> Type[S]:
        return self.struct_type.reconstruct(config)  # type: ignore


U = TypeVar("U", bound=Union)


@frozen()
class UnionData(Data[U]):
    union_type: Type[U] = field()

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> U:
        return self.compute_type(state.config)(state, address, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: U,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.compute_type(config).SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.compute_type(config).ALIGNMENT

    def compute_type(self, config: PlatformConfig) -> Type[U]:
        return self.union_type.reconstruct(config)  # type: ignore


@final
@frozen()
class CreateStruct:
    packed: bool = DEFAULT_PACKED
    virtual: bool = DEFAULT_VIRTUAL
    config: PlatformConfig = SYSTEM_PLATFORM_CONFIG

    def __call__(self, struct_type: TS) -> TS:
        packed = self.packed
        virtual = self.virtual
        config = self.config

        struct_type.PACKED = packed
        struct_type.VIRTUAL = virtual

        fields = fetch_fields(struct_type)

        class new_struct_type(struct_type):  # type: ignore
            pass

        offset = 0
        size = 0

        if packed:
            for name, field in fields.items():
                field.offset = offset

                field_size = field.data.compute_size(config)

                offset += field_size
                size += field_size

            new_struct_type.SIZE = size
            new_struct_type.ALIGNMENT = DEFAULT_ALIGNMENT

        else:
            new_struct_type.ALIGNMENT = alignment = max(
                (field.data.compute_alignment(config) for field in fields.values()),
                default=DEFAULT_ALIGNMENT,
            )

            for name, field in fields.items():
                # if the field has null alignment, move onto the next one

                field_alignment = field.data.compute_alignment(config)

                if not field_alignment:
                    continue

                remain_size = size % field_alignment

                # if the size is not divisible by the alignment of the field, pad accordingly

                if remain_size:
                    pad_size = field_alignment - remain_size

                    offset += pad_size
                    size += pad_size

                field_size = field.data.compute_size(config)

                field.offset = offset

                offset += field_size
                size += field_size

            if alignment:
                remain_size = size % alignment

                if remain_size:
                    pad_size = alignment - remain_size

                    offset += pad_size
                    size += pad_size

            new_struct_type.SIZE = size

        for name, field in fields.items():
            set_attribute(new_struct_type, name, field)

        set_name(new_struct_type, get_name(struct_type))  # type: ignore
        set_module(new_struct_type, get_module(struct_type))  # type: ignore

        return new_struct_type  # type: ignore


def struct(
    packed: bool = DEFAULT_PACKED,
    virtual: bool = DEFAULT_VIRTUAL,
    config: PlatformConfig = SYSTEM_PLATFORM_CONFIG,
) -> CreateStruct:
    return CreateStruct(packed, virtual, config)


@final
@frozen()
class CreateUnion:
    config: PlatformConfig = SYSTEM_PLATFORM_CONFIG

    def __call__(self, union_type: TU) -> TU:
        config = self.config

        fields = fetch_fields(union_type)

        class new_union_type(union_type):  # type: ignore
            pass

        new_union_type.SIZE = max(
            (field.data.compute_size(config) for field in fields.values()),
            default=DEFAULT_SIZE,
        )
        new_union_type.ALIGNMENT = max(
            (field.data.compute_alignment(config) for field in fields.values()),
            default=DEFAULT_ALIGNMENT,
        )

        for name, field in fields.items():
            set_attribute(new_union_type, name, field)

        set_name(new_union_type, get_name(union_type))  # type: ignore
        set_module(new_union_type, get_module(union_type))  # type: ignore

        return new_union_type  # type: ignore


def union(config: PlatformConfig = SYSTEM_PLATFORM_CONFIG) -> CreateUnion:
    return CreateUnion(config)


from gd.memory.fields import fetch_fields
