from pathlib import Path
import functools
import os

from ..utils._async import run_blocking_io
from ..utils.crypto.coders import Coder
from ..utils.wrap_tools import make_repr

from .save import SaveAPI

__all__ = ('SaveLoader', 'path')


try:
    local_env = os.getenv('localappdata')
    path = Path(local_env) / 'GeometryDash'

except Exception:
    path = Path()


class SaveLoader:
    def __init__(
        self, path: Path = path, main_file_name: str = 'CCGameManager.dat',
        level_file_name: str = 'CCLocalLevels.dat'
    ):
        self.main_data_file = path / main_file_name
        self.level_data_file = path / level_file_name

    def __repr__(self):
        info = {
            'main': self.main_data_file,
            'level': self.level_data_file
        }
        return make_repr(self, info)

    def __call__(self, *args, **kwargs):
        return self.local()

    async def local(self):
        return await run_blocking_io(self._local)

    async def from_string(self, main_stream, level_stream, xor: bool = True):
        return await run_blocking_io(
            functools.partial(self._load, main_stream, level_stream, xor=xor)
        )

    def make_api(self, main, levels):
        return SaveAPI(main, levels)

    def _decode(self, stream, xor: bool = True):
        if isinstance(stream, str):
            stream = stream.encode()

        return Coder.decode_save(stream, needs_xor=xor).decode(errors='replace')

    def _load(self, main_stream, level_stream, xor: bool = True):
        main = self._decode(main_stream, xor=xor)
        levels = self._decode(level_stream, xor=xor)
        return SaveAPI(main, levels)

    def _local(self):
        try:
            parts = []

            for file in (self.main_data_file, self.level_data_file):

                with open(file, 'rb') as data_file:
                    parts.append(data_file.read())

            return self._load(*parts)

        except FileNotFoundError:
            print('Failed to find save files in the path: {!r}.'.format(str(path)))


SaveLoader = SaveLoader()
