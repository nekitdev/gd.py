from ..utils._async import run_blocking_io
from ..utils.wrap_tools import make_repr
from ..utils.crypto.coders import Coder

__all__ = ('SavePart', 'SaveAPI')


class SavePart(str):
    def __repr__(self):
        info = {
            'data': repr('... (len: {})'.format(len(self)))
        }
        return make_repr(self, info)

    async def parse(self):
        return await run_blocking_io(self._parse)

    def _parse(self):
        pass

    def _encode(self, xor: bool = True):
        return Coder.encode_save(self.encode(), needs_xor=xor)


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
