from .generator import SpriteGenUtil, SpriteGen, test_path, gen_center_offset, fix_glow_color, predict_color, reorder
from ..iconset import IconSet

gco = gen_center_offset
sg = SpriteGen(); sgu = SpriteGenUtil()
img = sg.load_image()
full_test = [
    IconSet(color_1 = 10, color_2 = 3, icon_robot = i) for i in range(1,27)
]
parsed = sgu.parse_xml()
full_bases = [
    sgu.find_bases(iconset) for iconset in full_test
]
full_related = [
    sgu.format_related(parsed, base_list) for base_list in full_bases
]
full_sprites = [
    sgu.retrieve_sprites(parsed, 'robot', elem) for elem in full_related
]
def make_sprite(typeof, splist, iconset) -> None:
    s = reorder(splist)
    ret = sg.make_blank()
    colors = iconset.get_colors()
    for sprite in s:
        color = predict_color(sprite, colors)
        sp = sg.get_sprite_image(img, sprite)
        offset = gco(ret, sp, sprite.offset)
        if color is not None:
            sp = sg.color(sp, color)
        if s.index(sprite) is 0:
            ret.paste(sp, offset)
        else:
            ret.alpha_composite(sp, offset)
    ret.save(test_path)

import time
for i in range(26):
    make_sprite('robot', full_sprites[i], full_test[i])
    time.sleep(1.5)

#make_sprite('wave', full_sprites[34], full_test[34])