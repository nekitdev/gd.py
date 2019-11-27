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

    def move_levels_down(self, to: int = 1, *, key: str = 'GLM_01', prefix: str = 'k_'):
        assert to >= 0
        try:
            inner = self.levels[key]

        except KeyError:
            return

        else:
            for _ in range(to):
                for k, v in inner.copy().items():
                    n = str(int(k.lstrip(prefix))+1)
                    inner[prefix+n] = v

            for n in range(to):
                inner[prefix+str(n)] = {}

    def as_tuple(self):
        return (self.main, self.levels)
