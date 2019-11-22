from .enums import *
from .loader import *
from .object import *
from .save import *

from . import loader

def change_path(path):
    loader.path = path
