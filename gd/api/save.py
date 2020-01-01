import json

from ..utils.wrap_tools import make_repr
from ..utils.xml_parser import *
from ..utils.crypto.coders import Coder

from .struct import *
from .utils import get_default

__all__ = ('Part', 'Database', 'LevelCollection')


class LevelCollection(list):
    def __init__(self, *args):
        if len(args) == 1:
            args = args[0]
        super().__init__(args)
        self._callback = None

    def __repr__(self):
        return self.__class__.__name__ + super().__repr__()

    @classmethod
    def launch(cls, caller, iterable):
        self = cls(iterable)
        self._callback = caller
        return self

    def _conf_api(self, api):
        if api is None:
            return self._callback
        return api

    def dump(self, api=None):
        api = self._conf_api(api)
        api.dump_my_levels(self)

    def dump_to_saved(self, api=None):
        api = self._conf_api(api)
        api.dump_saved_levels(self)


class Part(dict):
    def __init__(self, string: str = '', default: dict = None):
        self.parser = XMLParser()  # from utils.xml_parser
        try:
            loaded = self.parser.load(string)

        except Exception:
            if default is None:
                default = {}

            loaded = default

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
        self.main = Part(main, get_default('main'))
        self.levels = Part(levels, get_default('levels'))

    def __repr__(self):
        info = {
            'main': repr(self.main),
            'levels': repr(self.levels)
        }
        return make_repr(self, info)

    def __json__(self):
        return self.as_tuple()

    def get_username(self):
        return self.main.get('GJA_001')

    def get_password(self):
        return self.main.get('GJA_002')

    def get_account_id(self):
        return self.main.get('GJA_003')

    def get_player_id(self):
        return self.main.get('playerUserID')

    def get_udid(self):
        return self.main.get('playerUDID')

    def get_bootup_amount(self):
        return self.main.get('bootups')

    def _get_failsafe(self, key: str, is_level_part: bool = True, default: object = None):
        part = self.levels if is_level_part else self.main

        if default is None:
            default = {}

        if key not in part:
            part[key] = default

        return part[key]

    def _to_levels(self, level_dicts):
        return LevelCollection.launch(self, map(LevelAPI.from_mapping,
            filter(lambda thing: isinstance(thing, dict), level_dicts)
        ))

    def load_saved_levels(self, *, key: str = 'GLM_03'):
        inner = self._get_failsafe(key, is_level_part=False)
        return self._to_levels(inner.values())

    def dump_saved_levels(self, levels: list, *, key: str = 'GLM_03'):
        self.main[key] = {str(level.id): level.to_map() for level in levels}

    def load_my_levels(self, *, key: str = 'LLM_01'):
        inner = self._get_failsafe(key)
        return self._to_levels(inner.values())

    def dump_my_levels(self, levels: list, *, key: str = 'LLM_01', prefix: str = 'k_'):
        stuff = {'_isArr': True}
        stuff.update(
            {prefix + str(n): level.to_map() for n, level in enumerate(levels)}
        )
        self.levels[key] = stuff

    def dump(self):
        from .loader import save  # I hate circular imports. - nekit
        save.dump(self)

    def as_tuple(self):
        return (self.main, self.levels)
