from .graphics.colors import colors

class IconSet:
    def __init__(self, **options):
        self.options = options
    
    def __str__(self):
        glow_outline = 'On' if self.has_glow_outline() else 'Off'
        res = f'[gd.IconSet]\n[Icons]\n[Main:{self.main}][Type:{self.main_type}]\n[Cube:{self.cube}]\n[Ship:{self.ship}]\n[Ball:{self.ball}]\n[Ufo:{self.ufo}]\n[Wave:{self.wave}]\n[Robot:{self.robot}]\n[Spider:{self.spider}]\n[Colors]\n[Color_1:{self.color_1.to_hex()}]\n[Color_2:{self.color_2.to_hex()}]\n[Glow_Outline:{glow_outline}]'
        return res
    
    @property
    def main(self):
        return self.options.get('main_icon')
    @property
    def color_1(self):
        return colors.get(self.options.get('color_1'), None)
    @property
    def color_2(self):
        return colors.get(self.options.get('color_2'), None)
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