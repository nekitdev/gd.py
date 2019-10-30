from .colors import Colour

from .utils.enums import IconType
from .utils.wrap_tools import make_repr

class IconSet:
    """Class that represents an Icon Set."""
    def __init__(self, **options):
        self.options = options

    def __repr__(self):
        info = {
            'main_icon': self.main,
            'main_type': self.main_type,
            'color_1': self.color_1,
            'color_2': self.color_2
        }
        return make_repr(self, info)

    @property
    def main(self):
        """:class:`int`: ID of the main icon of the iconset. (see :attr:`.IconSet.main_type`)"""
        return self.options.get('main_icon', 1)

    @property
    def color_1(self):
        """:class:`.Colour`: A first color of the iconset."""
        return self.options.get('color_1', Colour(0x00ff00))

    @property
    def color_2(self):
        """:class:`.Colour`: A second color of the iconset."""
        return self.options.get('color_2', Colour(0x00ffff))

    @property
    def main_type(self):
        """:class:`.IconType`: A type of the main icon of the iconset."""
        return self.options.get('main_icon_type', IconType(0))

    @property
    def cube(self):
        """:class:`int`: Cube ID of the iconset."""
        return self.options.get('icon_cube', 1)

    @property
    def ship(self):
        """:class:`int`: Ship ID of the iconset."""
        return self.options.get('icon_ship', 1)

    @property
    def ball(self):
        """:class:`int`: Ball ID of the iconset."""
        return self.options.get('icon_ball', 1)

    @property
    def ufo(self):
        """:class:`int`: UFO ID of the iconset."""
        return self.options.get('icon_ufo', 1)

    @property
    def wave(self):
        """:class:`int`: Wave ID of the iconset."""
        return self.options.get('icon_wave', 1)

    @property
    def robot(self):
        """:class:`int`: Robot ID of the iconset."""
        return self.options.get('icon_robot', 1)

    @property
    def spider(self):
        """:class:`int`: Spider ID of the iconset."""
        return self.options.get('icon_spider', 1)

    @property
    def explosion(self):
        """:class:`int`: Explosion ID of the iconset."""
        return self.options.get('icon_explosion', 1)

    def has_glow_outline(self):
        """:class:`bool`: Indicates whether an iconset has glow outline."""
        return self.options.get('has_glow_outline', False)

    def get_colors(self):
        """Tuple[:class:`.Colour`, :class:`.Colour`]: A shorthand for *color_1* and *color_2*."""
        return self.color_1, self.color_2
