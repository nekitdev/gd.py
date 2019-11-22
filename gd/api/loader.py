from pathlib import Path
import functools
import os

from ..utils._async import run_blocking_io
from ..utils.crypto.coders import Coder
from ..utils.wrap_tools import make_repr

from .save import SaveAPI

__all__ = (
    'SaveUtil', 'path', 'util', 'load_save', 'dump_save',
    'from_string', 'to_string', 'make_api')


try:
    local_env = os.getenv('localappdata')
    path = Path(local_env) / 'GeometryDash'

except Exception:
    path = Path()


class SaveUtil:
    def __init__(
        self, path: Path = path, main_file_name: str = 'CCGameManager.dat',
        level_file_name: str = 'CCLocalLevels.dat'
    ):
        self.main = main_file_name
        self.level = level_file_name

    def __repr__(self):
        info = {
            'main': self.main_data_file,
            'level': self.level_data_file
        }
        return make_repr(self, info)

    @property
    def main_data_file(self):
        return path / self.main

    @property
    def level_data_file(self):
        return path / self.level

    async def local_load(self):
        return await run_blocking_io(self._local_load)

    async def local_dump(self, api: SaveAPI):
        await run_blocking_io(self._local_dump, api)

    async def to_string(self, api: SaveAPI, connect: bool = True, xor: bool = False):
        return await run_blocking_io(
            functools.partial(self._dump, api, connect=connect, xor=xor)
        )

    async def from_string(self, main_stream, level_stream, xor: bool = False):
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

    def _dump(self, api, connect: bool = True, xor: bool = False):
        parts = []

        for part in api.as_tuple():
            parts.append(part.encode(xor=xor).decode())

        main, levels, *_ = parts

        if connect:
            return main + ';' + levels
        else:
            return main, levels

    def _local_load(self):
        try:
            parts = []

            for file in (self.main_data_file, self.level_data_file):

                with open(file, 'rb') as data_file:
                    parts.append(data_file.read())

            return self._load(*parts)

        except FileNotFoundError:
            print('Failed to find save files in the path: {!r}.'.format(str(path)))

    def _local_dump(self, api: SaveAPI):
        files = (self.main_data_file, self.level_data_file)

        for file, part in zip(files, api.as_tuple()):

            with open(file, 'wb') as data_file:
                data_file.write(part.encode())


util = SaveUtil()
load_save = util.local_load
dump_save = util.local_dump
from_string = util.from_string
to_string = util.to_string
make_api = util.make_api
