from .sprite import Sprite
from .size_offset import SizeOffsetTuple
from PIL import Image
import xml
import pkg_resources

main_path = 'resources/GJ_GameSheet02-uhd'

def make_path(form):
    return pkg_resources.resource_filename(__name__, main_path + form)

class SpriteGen:
    def __init__(self):
        self.image_path = make_path('.png')
        self.plist_path = make_path('.plist')

    def load_image(self):
        image = Image.open(self.image_path)
        return image