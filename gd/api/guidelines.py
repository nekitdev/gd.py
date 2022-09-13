from __future__ import annotations

from typing import BinaryIO, Dict, Type, TypeVar

from gd.binary import VERSION
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder, GuidelineColor
from gd.models_utils import concat_guidelines, split_guidelines

__all__ = ("Guidelines",)

G = TypeVar("G", bound="Guidelines")


class Guidelines(Dict[float, GuidelineColor]):
    def add(self, timestamp: float, color: GuidelineColor = GuidelineColor.DEFAULT) -> None:
        self[timestamp] = color

    @classmethod
    def from_binary(
        cls: Type[G], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> G:
        reader = Reader(binary)

        length = reader.read_u32(order)

        color = GuidelineColor

        return cls({reader.read_f32(order): color(reader.read_f32(order)) for _ in range(length)})

    def to_binary(
        self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u32(len(self))

        for timestamp, color in self.items():
            writer.write_f32(timestamp)
            writer.write_f32(color.value)

    @classmethod
    def from_robtop(cls: Type[G], string: str) -> G:
        color = GuidelineColor

        return cls(
            {timestamp: color(value) for timestamp, value in split_guidelines(string).items()}
        )

    def to_robtop(self) -> str:
        return concat_guidelines({timestamp: color.value for timestamp, color in self.items()})
