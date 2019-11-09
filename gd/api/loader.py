from pathlib import Path
import functools
import os
import traceback

from ..utils._async import run_blocking_io

from ..utils.crypto.coders import Coder

from ..utils.wrap_tools import make_repr

from .save import SaveAPI

__all__ = ('SaveLoader', 'path')


path = Path()

try:
    local_path = Path(os.getenv('localappdata'))
    path = local_path / 'GeometryDash'

except Exception:
    pass


class SaveLoader:
    main_data_file = 'CCGameManager.dat'
    level_data_file = 'CCLocalLevels.dat'

    def __repr__(self):
        info = {
            'main': self.main_data_file,
            'level': self.level_data_file
        }
        return make_repr(self, info)

    def __call__(self, *args, **kwargs):
        return self.local()

    @classmethod
    async def local(cls):
        return await run_blocking_io(cls._local)

    @classmethod
    async def from_string(cls, main_stream, level_stream, xor: bool = True):
        return await run_blocking_io(
            functools.partial(cls._load, main_stream, level_stream, xor=xor)
        )

    @classmethod
    def make_api(cls, main, levels):
        return SaveAPI(main, levels)

    @classmethod
    def _decode(cls, stream, xor: bool = True):
        if isinstance(stream, str):
            stream = stream.encode()

        return Coder.decode_save(stream, needs_xor=xor).decode(errors='replace')

    @classmethod
    def _load(cls, main_stream, level_stream, xor: bool = True):
        main = cls._decode(main_stream, xor=xor)
        levels = cls._decode(level_stream, xor=xor)
        return SaveAPI(main, levels)

    @classmethod
    def _local(cls):
        try:
            parts = []

            for file in (cls.main_data_file, cls.level_data_file):

                with open(path/file, 'rb') as data_file:
                    parts.append(data_file.read())

            return cls._load(*parts)

        except FileNotFoundError:
            print('Failed to find save files in the path: {!r}.'.format(str(path)))


SaveLoader = SaveLoader()
