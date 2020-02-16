from .typing import Tuple, Union

from .abstractentity import AbstractEntity
from .colors import Color

from .utils.enums import IconType
from .utils.text_tools import make_repr


class IconSet(AbstractEntity):
    """Class that represents an Icon Set."""

    def __repr__(self) -> str:
        info = {
            'main_icon': self.main,
            'main_type': self.main_type,
            'color_1': self.color_1,
            'color_2': self.color_2
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return 'IconSet({}, {})'.format(self.color_1, self.color_2)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.options == other.options

    def _json(self) -> dict:
        return self.options

    @property
    def id(self) -> int:
        return self.main + self.color_1.value + self.color_2.value + self.main_type.value

    @property
    def main(self) -> int:
        """:class:`int`: ID of the main icon of the iconset. (see :attr:`.IconSet.main_type`)"""
        return self.options.get('main_icon', 1)

    @property
    def color_1(self) -> Color:
        """:class:`.Color`: A first color of the iconset."""
        return self.options.get('color_1', Color(0x00ff00))

    @property
    def color_2(self) -> Color:
        """:class:`.Color`: A second color of the iconset."""
        return self.options.get('color_2', Color(0x00ffff))

    @property
    def main_type(self) -> IconType:
        """:class:`.IconType`: A type of the main icon of the iconset."""
        return IconType.from_value(self.options.get('main_icon_type', 0))

    @property
    def cube(self) -> int:
        """:class:`int`: Cube ID of the iconset."""
        return self.options.get('icon_cube', 1)

    @property
    def ship(self) -> int:
        """:class:`int`: Ship ID of the iconset."""
        return self.options.get('icon_ship', 1)

    @property
    def ball(self) -> int:
        """:class:`int`: Ball ID of the iconset."""
        return self.options.get('icon_ball', 1)

    @property
    def ufo(self) -> int:
        """:class:`int`: UFO ID of the iconset."""
        return self.options.get('icon_ufo', 1)

    @property
    def wave(self) -> int:
        """:class:`int`: Wave ID of the iconset."""
        return self.options.get('icon_wave', 1)

    @property
    def robot(self) -> int:
        """:class:`int`: Robot ID of the iconset."""
        return self.options.get('icon_robot', 1)

    @property
    def spider(self) -> int:
        """:class:`int`: Spider ID of the iconset."""
        return self.options.get('icon_spider', 1)

    @property
    def explosion(self) -> int:
        """:class:`int`: Explosion ID of the iconset."""
        return self.options.get('icon_explosion', 1)

    def has_glow_outline(self) -> bool:
        """:class:`bool`: Indicates whether an iconset has glow outline."""
        return self.options.get('has_glow_outline', False)

    def get_colors(self) -> Tuple[Color, Color]:
        """Tuple[:class:`.Color`, :class:`.Color`]: A shorthand for *color_1* and *color_2*."""
        return self.color_1, self.color_2

    async def generate(self, type: Union[int, str, IconType] = 'cube') -> bytes:
        return await self.client.generate_icon(type, self)
