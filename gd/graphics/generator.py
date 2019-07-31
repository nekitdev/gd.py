import pkg_resources
from xml.etree import ElementTree

from PIL import Image, ImageOps

from .sprite import Sprite, Rectangle
from ..iconset import IconSet
from .colors import colors
from ..errors import error

main_path = 'resources/GJ_GameSheet02-uhd'

test_path = pkg_resources.resource_filename(__name__, 'resources/result.png')

def make_path(form):
    return pkg_resources.resource_filename(__name__, main_path + form)


class SpriteGenUtil:
    def __init__(self):
        self.plist_path = make_path('.plist')
        self.icon_types = ['cube', 'ship', 'ball', 'ufo', 'wave', 'robot', 'spider']

    def parse_xml(self):  # parsing xml into nice python dict
        parsed = ElementTree.parse(self.plist_path)
        load_dict = {}
        something = parsed.getroot()
        for i in range(2):  # going deeper into the tree
            something = something.getchildren()[i]
        for j in range(0, len(something.getchildren()), 2):
            temp = something[j].text
            start = something[j+1].getchildren()
            formatted = {
                'spriteOffset': parse_array(start[3]),
                'spriteSize': parse_array(start[5]),
                'spriteSourceSize': parse_array(start[7]),
                'spriteUpLeftCorner': parse_array(start[9], deep=0),
                'spriteRect': Rectangle(*parse_array(start[9], deep=1)),
                'isRotated': parse_bool(start[11])
            }
            load_dict[temp] = formatted
        return load_dict

    def find_bases(self, iconset: IconSet): #finding bases for further creating
        final = []
        for icon in self.icon_types:
            temp = getattr(iconset, icon)
            temp = fix_int(temp)
            prefix = fix_prefix(icon)
            base = f"{prefix}_{temp}_..._001.png"
            final.append(base)
        return final
    
    def format_related(self, parsed_xml, base_list):  # getting all sprites related to bases
        final = {}; keys = list(parsed_xml.keys())
        for base in base_list:
            start = base.split('...')[0]
            temp = [key for key in keys if (key.startswith(start))]
            icon_type = self.icon_types[base_list.index(base)]
            final[icon_type] = temp
        return final
    
    def to_sprite_object(self, name, info_dict):  # converting dict to gd.graphics.Sprite
        sprite = None; id_index = (1 if 'ball' not in name else 2)
        if info_dict:
            sprite = Sprite(
                name = name, id = int(name.split('_')[id_index]),
                offset = info_dict.get('spriteOffset'),
                size = info_dict.get('spriteSize'),
                source_size = info_dict.get('spriteSourceSize'),
                upleft_corner = info_dict.get('spriteUpLeftCorner'),
                rectangle = info_dict.get('spriteRect'),
                is_rotated = info_dict.get('isRotated')
            )
        return sprite

    def retrieve_sprites(self, parsed_xml, icon_type, related_dict): #getting a list of gd.graphics.Sprite objects
        related_list = related_dict.get(icon_type); store = []
        for element in related_list:
            temp = parsed_xml.get(element)
            sprite = self.to_sprite_object(element, temp)
            store.append(sprite)
        return store

class SpriteGen:
    def __init__(self):
        self.image_path = make_path('.png')

    def load_image(self): #loading sprite sheet image
        image = Image.open(self.image_path)
        return image
    
    def apply_color(self, pixel, color):
        res = []
        for a, b in zip(pixel, color.to_rgba()):
            res.append(
                int(b/(255/a)) if a > 20 else a
            )
        return tuple(res)
    
    def make_blank(self):
        gen = (0 for i in range(4))
        image = Image.new("RGBA", (250, 250), tuple(gen))  # making blank image, with alpha composite = 0
        return image
    
    def get_sprite_image(self, sheet, sprite):
        ulcX, ulcY = sprite.upleft_corner; shX, shY = sheet.size
        if 'robot' in sprite.name: fix_robot_offset(sprite)
        realX, realY = (
            sprite.size if not sprite.is_rotated() else sprite.size[::-1]
        )  # realX is sizeX if sprite is not rotated, else it is sizeY
        border = (ulcX, ulcY, (shX-(ulcX+realX)), (shY-(ulcY+realY)))
        image = ImageOps.crop(sheet, border)
        if sprite.is_rotated():
            deg = fix_degree(90)
            image = image.rotate(deg, expand=True)  # fix translation
        if hasattr(sprite, 'fix_rotation_deg'):
            deg = fix_degree(sprite.fix_rotation_deg)
            image = image.rotate(deg, expand=True)
        return image

    def color(self, img, color):
        pixels = img.load()
        x, y = img.size
        for i in range(x):
            for j in range(y):
                pixel = pixels[i,j]
                pixels[i,j] = self.apply_color(pixel, color)
        return img
            
    def make_sprite(self, typeof, sprite_list, iconset):
        cases = {
            'cube': self.make_cube, 'ship': self.make_ship,
            'ball': self.make_ball, 'ufo': self.make_ufo,
            'wave': self.make_wave, 'robot': self.make_robot,
            'spider': self.make_spider
        }
        if typeof not in cases:
            raise error.InvalidArgument()
        return cases.get(typeof)(sprite_list, iconset)

def gen_center_offset(main, to_paste, additional=(0,0)):
    mX, mY, pX, pY, aX, aY = main.size + to_paste.size + additional  # '+' here is concatenation of tuples
    baseX, baseY = (mX-pX)//2, (mY-pY)//2
    return baseX + aX, baseY - aY

def fix_glow_color(colors):
    color1, color2 = colors
    if color2.index == 15:
        color2 = colors[12] if color1.index == 15 else color1
    return color2

def predict_color(sprite, colors):
    color1, color2 = colors
    if '_glow_' in sprite.name:
        return fix_glow_color(colors)
    elif '_2_001' in sprite.name:
        return color2
    elif all(part not in sprite.name for part in ('extra', '_3_001')):
        return color1
        
def fix_robot_offset(sprite) -> None:
    id = sprite.id; name = sprite.name
    sX, sY = sprite.offset
    offX, offY = (0, 0)
    if str(id) + '_02_' in name:
        sprite.fix_rotation_deg = -45
        offX -= (50 if '001D' in name else 40)
        offY -= 20
        if '_2_' in name:
            cases = {
                id in (2, 5, 6, 8, 9, 11, 12, 15, 17, 24): (15, -5),
                id in (7, 10, 19, 20): (0, 7),
                id is 13: (10, -4), id == 18: (-1, -1),
                id in (21, 25): (12, 0), id == 22: (0, -5),
                id in (3, 26): (1, 0), id == 23: (-3, -2)
            }
            offTX, offTY = cases.get(True, (0, 0))
            offX += offTX; offY += offTY
    elif str(id) + '_03_' in name:
        sprite.fix_rotation_deg = 45
        offX -= (40 if '001D' in name else 30)
        offY -= (52 if (id is 21 and '_2_' not in name) else 60)
    elif str(id) + '_04_' in name:
        offX -= (10 if '001D' in name else 0)
        offY -= 70
    sprite.options['offset'] = (sX+offX, sY+offY)

def fix_spider_offset(sprite):
    pass

def reorder(splist):
    pass

def sign(number):
    return (-1 if number < 0 else (1 if number > 0 else 0))
    
def fix_degree(deg):
    new_deg = deg % 360 + (-sign(deg) * 360 if abs(deg) > 180 else 0)
    return new_deg
    
def parse_array(element, deep=-1):
    ret = eval(
        element.text.replace('{', '(').replace('}', ')')
    )
    if deep > -1:
        ret = ret[deep]
    return ret

def parse_bool(element):
    return bool(element.tag.replace('false', str())) #this will eventually give us real bools from strings

def fix_prefix(prefix):
    cases = {
        'cube': 'player',
        'ball': 'player_ball',
        'ufo': 'bird',
        'wave': 'dart'
    }
    return cases.get(prefix, prefix)

def fix_int(thing):
    return str(thing) if len(str(thing)) > 1 else f"0{thing}"
