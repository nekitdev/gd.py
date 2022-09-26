from builtins import setattr as set_attribute
from typing import ClassVar, Optional, Type, TypeVar

from attrs import define, field

from gd.memory.constants import DEFAULT_ALIGNMENT, DEFAULT_PACKED, DEFAULT_SIZE
from gd.memory.fields import fetch_fields
from gd.memory.state import AbstractState
from gd.platform import PlatformConfig
from gd.string_utils import tick
from gd.typing import ClassDecoratorIdentity

__all__ = ("Base", "Struct", "Union", "struct", "union")


@define()
class Base:
    ALIGNMENT: ClassVar[int] = DEFAULT_ALIGNMENT
    SIZE: ClassVar[int] = DEFAULT_SIZE

    state: AbstractState = field()
    address: int = field(repr=hex)

    @property
    def size(self) -> int:
        return type(self).SIZE

    @property
    def alignment(self) -> int:
        return type(self).ALIGNMENT


@define()
class Struct(Base):
    """Represents `struct` types."""

    PACKED: ClassVar[bool] = DEFAULT_PACKED


@define()
class Union(Base):
    """Represents `union` types."""


PAD_NAME = "__pad_{}__"

pad_name = PAD_NAME.format

FINAL = "final"

RESERVED_NAME = f"the field name can not be {tick(FINAL)}"


TS = TypeVar("TS", bound=Type[Struct])


def struct(
    packed: bool = DEFAULT_PACKED, config: Optional[PlatformConfig] = None
) -> ClassDecoratorIdentity[TS]:
    if config is None:
        config = PlatformConfig.system()

    def wrap(struct_type: TS) -> TS:
        fields = fetch_fields(struct_type)

        class new_struct_type(struct_type):
            pass

        new_struct_type.PACKED = packed

        offset = 0
        size = 0

        if packed:
            for name, field in fields.items():
                if name == FINAL:
                    raise ValueError(RESERVED_NAME)

                field.offset = offset

                field_size = field.compute_size(config)

                offset += field_size
                size += field_size

            new_struct_type.SIZE = size
            new_struct_type.ALIGNMENT = DEFAULT_ALIGNMENT

        else:
            new_struct_type.ALIGNMENT = alignment = max(
                field.compute_alignment(config) for field in fields.values()
            )

            field_array = list(fields.items())

            index = 0

            for main_name, main_field in fields.items():
                if main_name == FINAL:
                    raise ValueError(RESERVED_NAME)

                main_field.offset = offset

                main_size = main_field.compute_size(config)

                offset += main_size
                size += main_size

                # if the field has null alignment, move onto the next one

                main_alignment = main_field.compute_alignment(config)

                if not main_alignment:
                    continue

                before_size = 0

                # calculate the size of all fields preceding current field

                for _, field in field_array:
                    if field is main_field:
                        break

                    before_size += field.compute_size(config)

                remain_size = before_size % main_alignment

                # if the size is not divisible by the alignment of the field, pad accordingly

                if remain_size:
                    pad_size = main_alignment - remain_size

                    offset += pad_size
                    size += pad_size

                    name = pad_name(main_name)

                    field = ...

                    field_array.insert(index, (name, field))

                    index += 1

                index += 1

            fields = dict(field_array)

            if alignment:
                remain_size = size % alignment

                if remain_size:
                    pad_size = alignment - remain_size

                    offset += pad_size
                    size += pad_size

                    name = pad_name(FINAL)

                    field = ...

                    fields[name] = field

            new_struct_type.SIZE = size

        for name, field in fields.items():
            set_attribute(new_struct_type, name, field)

        return new_struct_type

    return wrap


TU = TypeVar("TU", bound=Type[Union])


def union(config: Optional[PlatformConfig] = None) -> ClassDecoratorIdentity[TU]:
    if config is None:
        config = PlatformConfig.system()

    def wrap(union_type: TU) -> TU:
        fields = fetch_fields(union_type)

        class new_union_type(union_type):
            pass

        new_union_type.SIZE = max(
            field.compute_size(config) for field in fields.values()
        )
        new_union_type.ALIGNMENT = max(
            field.compute_alignment(config) for field in fields.values()
        )

        for name, field in fields.items():
            set_attribute(new_union_type, name, field)

        return new_union_type

    return wrap
