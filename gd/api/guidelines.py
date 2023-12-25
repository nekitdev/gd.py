from __future__ import annotations

from typing import Dict, Type, TypeVar

from gd.enums import GuidelineColor
from gd.models_constants import GUIDELINES_SEPARATOR
from gd.models_utils import concat_guidelines, split_guidelines
from gd.robtop import RobTop

__all__ = ("Guidelines",)

G = TypeVar("G", bound="Guidelines")


class Guidelines(Dict[float, GuidelineColor], RobTop):
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
    def from_robtop(cls: Type[G], string: str) -> G:
        color = GuidelineColor

        return cls(
            {timestamp: color(value) for timestamp, value in split_guidelines(string).items()}
        )

    def to_robtop(self) -> str:
        return concat_guidelines({timestamp: color.value for timestamp, color in self.items()})

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return GUIDELINES_SEPARATOR in string
