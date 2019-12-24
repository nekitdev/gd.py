from pathlib import Path
import functools
import os
import sys

from ..utils._async import run_blocking_io
from ..utils.crypto.coders import Coder
from ..utils.wrap_tools import make_repr

from .save import Database

__all__ = (
    'SaveUtil', 'path', 'util', 'load_save', 'dump_save',
    'from_string', 'to_string', 'make_db', 'set_path')

MAIN = 'CCGameManager.dat'
LEVELS = 'CCLocalLevels.dat'


try:
    if sys.platform == 'win32':
        local_env = os.getenv('localappdata')
        path = Path(local_env) / 'GeometryDash'

    elif sys.platform == 'darwin': 
        local_env = os.getenv('HOME')
        path = Path(local_env) / 'Library' / 'Application Support' / 'Geometry Dash'
        # TODO: figure out encoding of MacOS GD saves (if possible)

    else:
        path = Path()    

except Exception:
    path = Path()


def set_path(new_path):
    global path
    path = new_path


class SaveUtil:
    def __repr__(self):
        return make_repr(self)

    async def local_load(self, *args, **kwargs):
        return await run_blocking_io(self._local_load, *args, **kwargs)

    async def local_dump(self, *args, **kwargs):
        await run_blocking_io(self._local_dump, *args, **kwargs)

    async def to_string(self, *args, **kwargs):
        return await run_blocking_io(
            functools.partial(self._dump, *args, **kwargs)
        )

    async def from_string(self, *args, **kwargs):
        return await run_blocking_io(
            functools.partial(self._load, *args, **kwargs)
        )

    def make_db(self, main: str = '', levels: str = ''):
        return Database(main, levels)

    def _decode(self, stream, xor: bool = True):
        if isinstance(stream, str):
            stream = stream.encode()

        try:
            return Coder.decode_save(stream, needs_xor=xor).decode(errors='replace')
        except Exception:
            return str()

    def _load(self, main_stream: str = '', level_stream: str = '', xor: bool = True):
        main = self._decode(main_stream, xor=xor)
        levels = self._decode(level_stream, xor=xor)
        return Database(main, levels)

    def _dump(self, db, connect: bool = True, xor: bool = False):
        parts = []

        for part in db.as_tuple():
            parts.append(part.encode(xor=xor).decode())

        main, levels, *_ = parts

        if connect:
            return main + ';' + levels
        else:
            return main, levels

    def _local_load(self, main_path=None, levels_path=None,
        default_main: str = MAIN, default_levels: str = LEVELS
    ):
        main_path = _config_path(main_path, default_main)
        levels_path = _config_path(levels_path, default_levels)

        try:
            parts = []

            for path in (main_path, levels_path):

                with open(path, 'rb') as file:
                    parts.append(file.read())

            return self._load(*parts)

        except OSError:
            print('Failed to find save files in given path.')

    def _local_dump(self, db: Database, main_path=None, levels_path=None,
        default_main: str = MAIN, default_levels: str = LEVELS
    ):
        main_path = _config_path(main_path, default_main)
        levels_path = _config_path(levels_path, default_levels)

        files = (main_path, levels_path)

        for file, part in zip(files, db.as_tuple()):

            with open(file, 'wb') as data_file:
                data_file.write(part.encode())


def _config_path(some_path, default):
    try:
        p = Path(some_path)

        if p.is_dir():
            return p / default

        return p

    except Exception:
        return path / default   


util = SaveUtil()
load_save = util.local_load
dump_save = util.local_dump
from_string = util.from_string
to_string = util.to_string
make_db = util.make_db
