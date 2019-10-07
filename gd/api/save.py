from ..utils.wrap_tools import make_repr
from ..utils.crypto.coders import Coder

__all__ = ('SavePart', 'SaveAPI')


class SavePart:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        info = {
            'data': repr('... (len: {})'.format(len(self.data)))
        }
        return make_repr(self, info)

    def __str__(self):
        return self.data

    def encode(self):
        return Coder.encode_save(self.data)


class SaveAPI:
    def __init__(self, main, levels):
        self.main = SavePart(main)
        self.levels = SavePart(levels)

    def __repr__(self):
        info = {
            'main': repr(self.main),
            'levels': repr(self.levels)
        }
        return make_repr(self, info)
