from .generator import SpriteGenUtil, SpriteGen, test_path, gen_center_offset, fix_glow_color, predict_color, reorder
from ..colors import colors
from ..iconset import IconSet
import time

gco = gen_center_offset
sg = SpriteGen(); sgu = SpriteGenUtil()
img = sg.load_image()
full_test = [
    IconSet(color_1 = colors[10], color_2 = colors[3], icon_cube = i) for i in range(1,100)
]
parsed = sgu.parse_xml()
full_bases = [
    sgu.find_bases(iconset) for iconset in full_test
]
full_related = [
    sgu.format_related(parsed, base_list) for base_list in full_bases
]
full_sprites = [
    sgu.retrieve_sprites(parsed, 'cube', elem) for elem in full_related
]
def make_sprite(typeof, splist, iconset) -> None:
    reorder(splist)
    s = splist
    if not iconset.has_glow_outline():
        s = [sp for sp in splist if '_glow_' not in sp.name]
    ret = sg.make_blank()
    colors = iconset.get_colors()
    for sprite in s:
        color = predict_color(sprite, colors)
        sp = sg.get_sprite_image(img, sprite)
        offset = gco(ret, sp, sprite.offset)
        if color is not None:
            sp = sg.color(sp, color)
        ret.alpha_composite(sp, offset)
    ret.save(test_path)
    time.sleep(1)

for i in range(100):
    make_sprite('cube', full_sprites[i], full_test[i])
