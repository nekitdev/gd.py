from typing import Iterator, Type, TypeVar

from attrs import frozen
from colors import Color as ColorCore  # fmt: skip
from iters.iters import iter, wrap_iter
from typing_extensions import Self
from wraps.option import Option
from wraps.wraps import wrap_optional

from gd.converters import CONVERTER
from gd.defaults.primitives.colors import DEFAULT_COLOR_1_ID, DEFAULT_COLOR_2_ID, DEFAULT_COLOR_3_ID
from gd.internals.primitives.colors import InternalColor
from gd.primitives.colors.mappings import VALUE_TO_ID

__all__ = ("Color",)


@frozen(order=True)
class Color(ColorCore):
    @property
    def id(self) -> Option[int]:
        """The ID of the color. [`Some(id)`][wraps.option.Some] if the color has an associated ID,
        otherwise [`NULL`][wraps.option.NULL].
        """
        return wrap_optional(VALUE_TO_ID.get(self.value))

    @classmethod
    def from_value(cls, value: int) -> Self:
        return cls(value)

    def into_value(self) -> int:
        return self.value

    @classmethod
    def default(cls) -> Self:
        return cls.white()

    @classmethod
    def default_color_1(cls) -> Self:
        return cls.with_id(DEFAULT_COLOR_1_ID).unwrap()

    @classmethod
    def default_color_2(cls) -> Self:
        return cls.with_id(DEFAULT_COLOR_2_ID).unwrap()

    @classmethod
    def default_color_3(cls) -> Self:
        return cls.with_id(DEFAULT_COLOR_3_ID).unwrap()

    @classmethod
    def with_id(cls, id: int) -> Option[Self]:
        """Returns the color with the given ID.

        Arguments:
            id: The ID of the color.

        Returns:
            [`Some(color)`][wraps.option.Some] if the color with the given ID exists,
                otherwise [`NULL`][wraps.option.NULL].
        """
        return wrap_optional(VALUE_TO_ID.get(id)).map(cls.from_value)

    @classmethod
    @wrap_iter
    def iter_colors(cls) -> Iterator[Self]:
        """Iterates over all in-game colors.

        Returns:
            The iterator over in-game colors.
        """
        return iter(VALUE_TO_ID).map(cls.from_value).unwrap()

    @classmethod
    def from_internal(cls, internal: InternalColor) -> Self:
        return cls.from_rgb(internal.red, internal.green, internal.blue)

    def into_internal(self) -> InternalColor:
        return InternalColor(self.red, self.green, self.blue)


C = TypeVar("C", bound="Color")


def unstructure_color(color: Color) -> int:
    return color.into_value()


def structure_color(value: int, color_type: Type[C]) -> C:
    return color_type.from_value(value)


CONVERTER.register_structure_hook(Color, structure_color)
CONVERTER.register_unstructure_hook(Color, unstructure_color)
