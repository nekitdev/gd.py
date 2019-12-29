import json

from ..utils.wrap_tools import make_repr
from ..utils.xml_parser import *

from ..utils.crypto.coders import Coder

__all__ = ('Part', 'Database')


class Part(dict):
    def __init__(self, string: str = ''):
        self.parser = XMLParser()  # from utils.xml_parser
        try:
            loaded = self.parser.load(string)

        except Exception:
            loaded = {}

        super().__init__(loaded)

    def __str__(self):
        return json.dumps(self, indent=4)

    def __repr__(self):
        string = super().__repr__()
        info = {
            'len': len(string)
        }
        return make_repr(self, info)

    def dump(self):
        return self.parser.dump(self)

    def encode(self, xor: bool = True):
        return Coder.encode_save(self.dump().encode(), needs_xor=xor)


class Database:
    def __init__(self, main: str = '', levels: str = ''):
        self.main = Part(main)
        self.levels = Part(levels)

    def __repr__(self):
        info = {
            'main': repr(self.main),
            'levels': repr(self.levels)
        }
        return make_repr(self, info)

    def free_index(self, index: int = 0, *, key: str = 'GLM_01', prefix: str = 'k_'):
        try:
            inner = self.levels[key]

        except KeyError:
            return

        else:
            stuff = list(inner.values())

            if index == -1:
                index = len(stuff)

            stuff.insert(index, dict())

            self.levels[key] = {
                prefix + str(i): d for i, d in enumerate(stuff)
            }

    def as_tuple(self):
        return (self.main, self.levels)
