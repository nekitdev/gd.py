from __future__ import annotations

from typing import ClassVar, Dict, Iterator, List, Optional, Type, TypeVar

from attrs import frozen
from colors import Color as ColorCore
from funcs.composition import compose_once
from iters.iters import iter, wrap_iter

from gd.constants import DEFAULT_COLOR_1_ID, DEFAULT_COLOR_2_ID
from gd.converter import CONVERTER
from gd.models_constants import COLOR_SEPARATOR
from gd.models_utils import concat_color, split_color
from gd.robtop import RobTop
from gd.string_utils import tick

__all__ = ("Color",)

C = TypeVar("C", bound="Color")

ID_NOT_PRESENT = "color with ID {} is not present"


@frozen(order=True)
class Color(RobTop, ColorCore):
    ID_TO_VALUE: ClassVar[Dict[int, int]] = {
        0: 0x7DFF00,
        1: 0x00FF00,
        2: 0x00FF7D,
        3: 0x00FFFF,
        4: 0x007DFF,
        5: 0x0000FF,
        6: 0x7D00FF,
        7: 0xFF00FF,
        8: 0xFF007D,
        9: 0xFF0000,
        10: 0xFF7D00,
        11: 0xFFFF00,
        12: 0xFFFFFF,
        13: 0xB900FF,
        14: 0xFFB900,
        15: 0x000000,
        16: 0x00C8FF,
        17: 0xAFAFAF,
        18: 0x5A5A5A,
        19: 0xFF7D7D,
        20: 0x00AF4B,
        21: 0x007D7D,
        22: 0x004BAF,
        23: 0x4B00AF,
        24: 0x7D007D,
        25: 0xAF004B,
        26: 0xAF4B00,
        27: 0x7D7D00,
        28: 0x4BAF00,
        29: 0xFF4B00,
        30: 0x963200,
        31: 0x966400,
        32: 0x649600,
        33: 0x009664,
        34: 0x006496,
        35: 0x640096,
        36: 0x960064,
        37: 0x960000,
        38: 0x009600,
        39: 0x000096,
        40: 0x7DFFAF,
        41: 0x7D7DAF,
    }

    VALUE_TO_ID: ClassVar[Dict[int, int]] = {value: id for id, value in ID_TO_VALUE.items()}

    @property
    def id(self) -> Optional[int]:
        """The in-game ID of the color (if present)."""
        return self.VALUE_TO_ID.get(self.value)

    @classmethod
    def from_data(cls: Type[C], data: int) -> C:
        return cls(data)

    def into_data(self) -> int:
        return self.value

    @classmethod
    def default(cls: Type[C]) -> C:
        return cls.white()

    @classmethod
    def default_color_1(cls: Type[C]) -> C:
        return cls.with_id(DEFAULT_COLOR_1_ID)

    @classmethod
    def default_color_2(cls: Type[C]) -> C:
        return cls.with_id(DEFAULT_COLOR_2_ID)

    @classmethod
    def from_robtop(cls: Type[C], string: str) -> C:
        r, g, b = iter(split_color(string)).map(compose_once(round, float)).tuple()  # type: ignore

        return cls.from_rgb(r, g, b)

    @staticmethod
    def can_be_in(string: str) -> bool:
        return COLOR_SEPARATOR in string

    def to_robtop(self) -> str:
        return iter.of(self.red, self.green, self.blue).map(str).collect(concat_color)

    @classmethod
    def with_id(cls: Type[C], id: int, default: Optional[C] = None) -> C:
        """Creates a [`Color`][gd.color.Color] with an in-game ID of `id`.

        Arguments:
            id: The in-game ID of the color.
            default: The default color to use. If not given, [`ValueError`][ValueError] is raised.

        Raises:
            ValueError: The color ID is not present and `default` is not provided.

        Returns:
            The [`Color`][gd.color.Color] matching the `id`.
        """
        value = cls.ID_TO_VALUE.get(id)

        if value is None:
            if default is None:
                raise ValueError(ID_NOT_PRESENT.format(tick(id)))

            return default

        return cls(value)

    @classmethod
    @wrap_iter
    def iter_colors(cls: Type[C]) -> Iterator[C]:
        """Returns an iterator over all in-game colors.

        Returns:
            An iterator over in-game colors.
        """
        return iter(cls.VALUE_TO_ID).map(cls).unwrap()

    @classmethod
    def list_colors(cls: Type[C]) -> List[C]:
        """Same as [`iter_colors`][gd.color.Color.iter_colors], but returns a list.

        Returns:
            The list of in-game colors.
        """
        return cls.iter_colors().list()


def dump_color(color: Color) -> int:
    return color.value


def load_color(value: int, color_type: Type[C]) -> C:
    return color_type(value)


CONVERTER.register_structure_hook(Color, load_color)
CONVERTER.register_unstructure_hook(Color, dump_color)
