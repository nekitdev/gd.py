from pathlib import Path
import os

from ..utils.crypto.coders import Coder

from .save import SaveAPI

__all__ = ('SaveLoader', 'path')


try:
    local_path = Path(os.getenv('localappdata'))
    path = local_path / 'GeometryDash'

except Exception as error:
    print(
        'Failed to load local Geometry Dash path. '
        'Error: [{0.__class__.__name__}: {0}]'.format(error)
    )


class SaveLoader:
    main_data = 'CCGameManager.dat'
    level_data = 'CCLocalLevels.dat'

    def __call__(self, *args, **kwargs):
        return self.local()

    @classmethod
    def local(cls):
        with open(path / cls.main_data, 'rb') as main_file:
            main = Coder.decode_save(main_file.read())

        with open(path / cls.level_data, 'rb') as level_file:
            levels = Coder.decode_save(level_file.read())

        return SaveAPI(main, levels)

SaveLoader = SaveLoader()
