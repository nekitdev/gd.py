from __future__ import annotations

from typing import Dict, Type, TypeVar

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ROUNDING
from gd.enums import ByteOrder, GuidelineColor
from gd.models_constants import GUIDELINES_SEPARATOR
from gd.models_utils import concat_guidelines, split_guidelines
from gd.robtop import RobTop

__all__ = ("Guidelines",)

G = TypeVar("G", bound="Guidelines")


class Guidelines(Dict[float, GuidelineColor], RobTop, Binary):
    """Represents guidelines.

    Binary:
        ```rust
        struct Guideline {
            timestamp: f32,
            color: f32,
        }

        struct Guidelines {
            guidelines_length: u32,
            guidelines: [Guideline; guidelines_length],
        }
        ```
    """

    def add(self, timestamp: float, color: GuidelineColor = GuidelineColor.DEFAULT) -> None:
        """Adds the guideline described by `timestamp` and `color`.

        Arguments:
            timestamp: The timestamp of the guideline.
            color: The color of the guideline.

        Example:
            ```python
            >>> guidelines = Guidelines()
            >>> guidelines.add(1.0, GuidelineColor.GREEN)
            >>> guidelines
            {1.0: <GuidelineColor.GREEN: 1.0>}
            ```
        """
        self[timestamp] = color

    @classmethod
    def from_binary(
        cls: Type[G],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> G:
        rounding = DEFAULT_ROUNDING

        reader = Reader(binary, order)

        length = reader.read_u32()

        read_f32 = reader.read_f32

        def read_f32_rounded(rounding: int = rounding) -> float:
            return round(read_f32(), rounding)

        color = GuidelineColor

        return cls({read_f32_rounded(): color(read_f32_rounded()) for _ in range(length)})

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

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

    @staticmethod
    def can_be_in(string: str) -> bool:
        return GUIDELINES_SEPARATOR in string
