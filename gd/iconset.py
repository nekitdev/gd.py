from .graphics.colors import colors
from .utils.wrap_tools import _make_repr

class IconSet:
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
        return self.options.get('main_icon')

    @property
    def color_1(self):
        return self.options.get('color_1')

    @property
    def color_2(self):
        return self.options.get('color_2')

    @property
    def main_type(self):
        return self.options.get('main_icon_type')

    @property
    def cube(self):
        return self.options.get('icon_cube')

    @property
    def ship(self):
        return self.options.get('icon_ship')

    @property
    def ball(self):
        return self.options.get('icon_ball')

    @property
    def ufo(self):
        return self.options.get('icon_ufo')

    @property
    def wave(self):
        return self.options.get('icon_wave')

    @property
    def robot(self):
        return self.options.get('icon_robot')

    @property
    def spider(self):
        return self.options.get('icon_spider')
    
    def has_glow_outline(self):
        return self.options.get('has_glow_outline')
    
    def get_colors(self):
        return self.color_1, self.color_2
