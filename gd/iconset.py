from .utils.wrap_tools import _make_repr

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
        return _make_repr(self, info)

    @property
    def main(self):
        """:class:`int` ID of the main icon of the iconset. (see :meth:`.IconSet.main_type`)"""
        return self.options.get('main_icon')

    @property
    def color_1(self):
        """:class:`.Colour`: A first color of the iconset."""
        return self.options.get('color_1')

    @property
    def color_2(self):
        """:class:`.Colour`: A second color of the iconset."""
        return self.options.get('color_2')

    @property
    def main_type(self):
        """:class:`.IconType`: A type of the main icon of the iconset."""
        return self.options.get('main_icon_type')

    @property
    def cube(self):
        """:class:`int`: Cube ID of the iconset."""
        return self.options.get('icon_cube')

    @property
    def ship(self):
        """:class:`int`: Ship ID of the iconset."""
        return self.options.get('icon_ship')

    @property
    def ball(self):
        """:class:`int`: Ball ID of the iconset."""
        return self.options.get('icon_ball')

    @property
    def ufo(self):
        """:class:`int`: UFO ID of the iconset."""
        return self.options.get('icon_ufo')

    @property
    def wave(self):
        """:class:`int`: Wave ID of the iconset."""
        return self.options.get('icon_wave')

    @property
    def robot(self):
        """:class:`int`: Robot ID of the iconset."""
        return self.options.get('icon_robot')

    @property
    def spider(self):
        """:class:`int`: Spider ID of the iconset."""
        return self.options.get('icon_spider')
    
    def has_glow_outline(self):
        """:class:`bool` Indicates whether an iconset has glow outline."""
        return self.options.get('has_glow_outline')
    
    def get_colors(self):
        """Tuple[:class:`.Colour`, :class:`.Colour`]: A shorthand for *color_1* and *color_2*."""
        return self.color_1, self.color_2
