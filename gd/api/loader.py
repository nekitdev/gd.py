from pathlib import Path
import functools
import os
import sys

from ..typing import Optional, Tuple, Union

from ..utils._async import run_blocking_io
from ..utils.crypto.coders import Coder
from ..utils.text_tools import make_repr

from .save import Database

__all__ = ('SaveUtil', 'get_path', 'save', 'make_db', 'set_path')

MAIN = 'CCGameManager.dat'
LEVELS = 'CCLocalLevels.dat'

PathLike = Optional[Union[str, Path]]

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


def set_path(new_path: Path) -> None:
    global path
    path = new_path


def get_path() -> Path:
    return path


class SaveUtil:
    def __repr__(self) -> str:
        return make_repr(self)

    async def load_async(self, *args, **kwargs) -> Database:
        return await run_blocking_io(self._local_load, *args, **kwargs)

    def load(self, *args, **kwargs) -> Database:
        return self._local_load(*args, **kwargs)

    async def dump_async(self, *args, **kwargs) -> None:
        await run_blocking_io(self._local_dump, *args, **kwargs)

    def dump(self, *args, **kwargs) -> None:
        return self._local_dump(*args, **kwargs)

    async def to_string_async(self, *args, **kwargs) -> str:
        return await run_blocking_io(
            functools.partial(self._dump, *args, **kwargs)
        )

    def to_string(self, *args, **kwargs) -> str:
        return self._dump(*args, **kwargs)

    async def from_string_async(self, *args, **kwargs) -> Database:
        return await run_blocking_io(
            functools.partial(self._load, *args, **kwargs)
        )

    def from_string(self, *args, **kwargs) -> Database:
        return self._load(*args, **kwargs)

    def make_db(self, main: str = '', levels: str = '') -> Database:
        return Database(main, levels)

    def _decode(self, stream: Union[bytes, str], xor: bool = True) -> str:
        if isinstance(stream, bytes):
            stream = stream.decode(errors='ignore')
        try:
            return Coder.decode_save(stream, needs_xor=xor)
        except Exception:
            return str()

    def _load(self, main: str = '', levels: str = '', xor: bool = True) -> Database:
        main = self._decode(main, xor=xor)
        levels = self._decode(levels, xor=xor)
        return Database(main, levels)

    def _dump(
        self, db: Database, connect: bool = True, xor: bool = False
    ) -> Union[str, Tuple[str, str]]:
        parts = []

        for part in db.as_tuple():
            parts.append(part.encode(xor=xor))

        main, levels, *_ = parts

        if connect:
            return main + ';' + levels
        else:
            return main, levels

    def _local_load(
        self, main: Optional[PathLike] = None, levels: Optional[PathLike] = None,
        default_main: PathLike = MAIN, default_levels: PathLike = LEVELS
    ) -> Database:
        main_path = _config_path(main, default_main)
        levels_path = _config_path(levels, default_levels)

        try:
            parts = []

            for path in (main_path, levels_path):

                with open(path, 'r') as file:
                    parts.append(file.read())

            return self._load(*parts)

        except OSError:
            return self.make_db()

    def _local_dump(
        self, db: Database, main: PathLike = None, levels: PathLike = None,
        default_main: PathLike = MAIN, default_levels: PathLike = LEVELS
    ) -> None:
        main_path = _config_path(main, default_main)
        levels_path = _config_path(levels, default_levels)

        files = (main_path, levels_path)

        for file, part in zip(files, db.as_tuple()):

            with open(file, 'w') as data_file:
                data_file.write(part.encode())


def _config_path(some_path: PathLike, default: PathLike) -> Path:
    try:
        p = Path(some_path)

        if p.is_dir():
            return p / default

        return p

    except Exception:
        return path / default


save = SaveUtil()
make_db = save.make_db
