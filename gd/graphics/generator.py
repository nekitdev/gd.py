'''A module for generating Geometry Dash Icon Set images.
Credits to Alex1304 for making the SpriteFactory in Java,
which is mostly translated by NeKitDS to Python.
[NOT WORKING YET]
'''
import ast
import pkg_resources
import re

from typing import List, Callable

from xml.etree import ElementTree

from PIL import Image, ImageOps

from .sprite import Sprite, Rectangle
from ..colors import Color, colors
from ..iconset import IconSet

main_path = 'resources/GJ_GameSheet02-uhd'

test_path = pkg_resources.resource_filename(__name__, 'resources/result.png')

def make_path(file_ext):
    return pkg_resources.resource_filename(__name__, main_path + file_ext)


class SpriteGenUtil:
    def __init__(self):
        self.plist_path = make_path('.plist')
        self.icon_types = ('cube', 'ship', 'ball', 'ufo', 'wave', 'robot', 'spider')

    def parse_xml(self):  # parsing xml into nice python dict
        parsed = ElementTree.parse(self.plist_path)
        load_dict = {}

        something = parsed.getroot()

        for i in range(2):  # going deeper into the tree
            something = something.getchildren()[i]

        for j in range(0, len(something.getchildren()), 2):

            temp = something[j].text
            start = something[j+1].getchildren()

            xy, wh = parse_array(start[9])

            formatted = {
                'spriteOffset': parse_array(start[3]),
                'spriteSize': parse_array(start[5]),
                'spriteSourceSize': parse_array(start[7]),
                'spriteRect': Rectangle(*xy, *wh),
                'isRotated': parse_bool(start[11])
            }
            load_dict[temp] = formatted

        return load_dict

    def find_bases(self, iconset: IconSet):  # finding bases for further creating
        final = []
        for icon in self.icon_types:
            temp = fix_int(getattr(iconset, icon))
            prefix = fix_prefix(icon)
            base = f'{prefix}_{temp}_..._001.png'
            final.append(base)
        return final

    def format_related(self, parsed_xml, base_list):  # getting all sprites related to bases
        final = {}
        for base in base_list:
            start = base.split('...')[0]
            temp = [key for key in parsed_xml.keys() if (key.startswith(start))]
            icon_type = self.icon_types[base_list.index(base)]
            final[icon_type] = temp
        return final

    def to_sprite_object(self, name, info_dict):  # converting dict to gd.graphics.Sprite
        sprite = None
        id_idx = (1 if 'ball' not in name else 2)
        if info_dict:
            sprite = Sprite(
                name = name.split('.')[0], id = int(name.split('_')[id_idx]),
                offset = info_dict.get('spriteOffset'),
                size = info_dict.get('spriteSize'),
                source_size = info_dict.get('spriteSourceSize'),
                upleft_corner = info_dict.get('spriteUpLeftCorner'),
                rectangle = info_dict.get('spriteRect'),
                is_rotated = info_dict.get('isRotated')
            )
        return sprite

    def retrieve_sprites(self, parsed_xml, icon_type, related_dict):  # getting a list of gd.graphics.Sprite objects
        related_list = related_dict.get(icon_type)
        store = []
        for element in related_list:
            temp = parsed_xml.get(element)
            sprite = self.to_sprite_object(element, temp)
            store.append(sprite)
        return store

class SpriteGen:
    def __init__(self):
        self.image_path = make_path('.png')

    def rotate(self, image, deg):
        deg = deg % 360 + (-sign(deg) * 360 if abs(deg) > 180 else 0)
        new = image.rotate(deg, expand=True)
        return new

    def reduce_brightness(self, image, sprite):
        pixels = image.load()
        x, y = image.size

        for i in range(x):
            for j in range(y):
                rgba = pixels[i, j]

                color_rgba = Color(0x808080).to_rgba()
                gen = (a&b for a, b in zip(rgba, color_rgba))

                pixels[i, j] = tuple(gen)

    def fix_brightness(self, image, sprite):
        if '001D' in sprite.name and '_glow_' not in sprite.name:
            self.reduce_brightness(image, sprite)

    def load_image(self):  # loading sprite sheet image
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
        t = (255, 255, 255, 0)
        image = Image.new('RGBA', (250, 250), t)
        return image

    def get_sprite_image(self, sheet, sprite):
        rect = sprite.get_rectangle()
        x, y = rect.get_coords()
        w, h = rect.size

        sx, sy = sheet.size

        if 'robot' in sprite.name:
            fix_robot_offset(sprite)

        rw, rh = (
            (w, h) if not sprite.is_rotated() else (h, w)
        )

        border = (x, y, sx-(x+rw), sy-(y+rh))

        print(border)

        image = ImageOps.crop(sheet, border)

        print(image)

        if hasattr(sprite, 'fix_rotation_deg'):
            image = self.rotate(image, sprite.fix_rotation_deg)

        if sprite.is_rotated():
            image = self.rotate(image, 90)

        self.fix_brightness(image, sprite)

        return image

    def color(self, img, color):
        pixels = img.load()
        x, y = img.size
        for i in range(x):
            for j in range(y):
                pixel = pixels[i, j]
                pixels[i, j] = self.apply_color(pixel, color)
        return img

def gen_center_offset(main, to_paste, sprite):
    name = sprite.name

    center_x, center_y = (n//2 for n in sprite.size)
    off_x, off_y = sprite.offset

    draw_x = 100 - center_x + off_x
    draw_y = 100 - center_y - off_y

    cases = {
        fix_prefix('robot') in name: (0, -20),
        fix_prefix('spider') in name: (6, -5),
        fix_prefix('ufo') in name: (0, 30)
    }

    draw_off_x, draw_off_y = cases.get(True, (0, 0))

    x, y = (25 + draw_off_x + draw_x), (25 + draw_off_y + draw_y)
    return x, y

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
    id = sprite.id
    name = sprite.name
    offX, offY = (0, 0)
    if str(id) + '_02_' in name:
        sprite.fix_rotation_deg = -45
        offX -= (50 if '001D' in name else 40)
        offY -= 20
        if '_2_' in name:
            cases = {
                id in (2, 5, 6, 8, 9, 11, 12, 15, 17, 24): (15, -5),
                id in (7, 10, 19, 20): (0, 7),
                id == 13: (10, -4), id == 18: (-1, -1),
                id in (21, 25): (12, 0), id == 22: (0, -5),
                id in (3, 26): (1, 0), id == 23: (-3, -2)
            }
            offTX, offTY = cases.get(True, (0, 0))
            offX += offTX
            offY += offTY
    elif str(id) + '_03_' in name:
        sprite.fix_rotation_deg = 45
        offX -= (40 if '001D' in name else 30)
        offY -= (52 if (id == 21 and '_2_' not in name) else 60)
    elif str(id) + '_04_' in name:
        offX -= (10 if '001D' in name else 0)
        offY -= 70
    print(offX, offY)
    sprite.update_offset(offX, offY)

def fix_spider_offset(sprite):
    pass

def reorder(splist):
    splist.reverse()
    push_sprite_to_back_if(splist, lambda sp: '_2_' in sp.name)
    pull_sprite_to_front_if(
        splist, lambda sp: re.match('(robot|spider)_[0-9]{2,3}_(02|03|04)_.*', sp.name) is not None
    )
    dupe_sprite_if(
        splist, lambda sp: re.match('robot_[0-9]{2,3}_(02|03|04)_.*', sp.name) is not None, 1
    )
    dupe_sprite_if(
        splist, lambda sp: re.match(
            'spider_[0-9]{2,3}_02_.*', sp.name) is not None and not 'extra' in sp.name, 2
    )
    pull_sprite_to_front_if(
        splist, lambda sp: re.match(
            'robot_[0-9]{2,3}_02_.*', sp.name) is not None and not sp.name.endswith('D')
    )
    pull_sprite_to_front_if(
        splist, lambda sp: re.match(
            'robot_[0-9]{2,3}_04_.*', sp.name) is not None and not sp.name.endswith('D')
    )
    push_sprite_to_back_if(splist, lambda sp: '_2_' not in sp.name and sp.name.endswith('D'))
    push_sprite_to_back_if(splist, lambda sp: '_2_' in sp.name and sp.name.endswith('D'))
    push_sprite_to_back_if(
        splist, lambda sp: re.match('spider_[0-9]{2,3}_04_.*', sp.name) is not None
    )
    pull_sprite_to_front_if(splist, lambda sp: 'extra' in sp.name)
    push_sprite_to_back_if(splist, lambda sp: '_glow_' in sp.name)
    push_sprite_to_back_if(splist, lambda sp: '_3_' in sp.name and 'bird' in sp.name)

def pull_sprite_to_front_if(splist: List[Sprite], predicate: Callable[[Sprite], bool]):
    offset = 0
    for i in range(len(splist)):
        sprite = splist[i-offset]
        if predicate(sprite):
            splist.pop(i-offset)
            splist.append(sprite)
            offset += 1

def push_sprite_to_back_if(splist: List[Sprite], predicate: Callable[[Sprite], bool]):
    for i in range(len(splist)):
        sprite = splist[i]
        if predicate(sprite):
            splist.pop(i)
            splist.insert(0, sprite)

def dupe_sprite_if(
    splist: List[Sprite], predicate: Callable[[Sprite], bool], dupe_n: int, front: bool = False
):
    ssize = len(splist)
    offset = 0
    for i in range(ssize):
        sprite = splist[i+offset]
        if predicate(sprite):
            dupe = sprite.duplicate()
            for i in range(dupe_n):
                if front:
                    splist.append(dupe)
                else:
                    splist.insert(0, dupe)
                    offset += 1
                dupe = dupe.duplicate()

def sign(number):
    return (-1 if number < 0 else (1 if number > 0 else 0))

def parse_array(element, deep=-1):
    ret = ast.literal_eval(
        element.text.replace('{', '(').replace('}', ')')
    )
    if deep > -1:
        ret = ret[deep]
    return ret

def parse_bool(element):
    return bool(element.tag.lower().replace('false', ''))  # this will eventually give us real bools from strings

def fix_prefix(prefix):
    cases = {
        'cube': 'player',
        'ball': 'player_ball',
        'ufo': 'bird',
        'wave': 'dart'
    }
    return cases.get(prefix, prefix)

def fix_int(n):
    return f'{n:02}' if n else n
