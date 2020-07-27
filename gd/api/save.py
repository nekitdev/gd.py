import collections

from attr import attrib, dataclass

from gd.typing import Any, Dict, Iterable, LevelCollection, List, Optional, Sequence, Tuple, Union

from gd.utils import search_utils as search
from gd.utils.text_tools import dumps, make_repr
from gd.utils.xml_parser import XMLParser

from gd.api.struct import LevelAPI
from gd.api.utils import get_default

__all__ = ("Part", "Database", "LevelCollection")


@dataclass
class Batch:
    completed: List[int] = attrib()
    stars: List[int] = attrib()
    demons: List[int] = attrib()

    @classmethod
    def create_empty(cls) -> Any:
        return cls(completed=[], stars=[], demons=[])


@dataclass
class Values:
    official: List[int] = attrib()
    normal: Batch = attrib()
    timely: Batch = attrib()
    gauntlet: Batch = attrib()
    packs: List[int] = attrib()

    def get_prefixes(self) -> Dict[str, List[int]]:
        values, normal, timely, gauntlet = self, self.normal, self.timely, self.gauntlet

        return {
            "n_": values.official,
            "c_": normal.completed,
            "d_": timely.completed,
            "g_": gauntlet.completed,
            "star_": normal.stars,
            "dstar_": timely.stars,
            "gstar_": gauntlet.stars,
            "demon_": normal.demons,
            "ddemon_": timely.demons,
            "gdemon_": gauntlet.demons,
            "pack_": values.packs,
        }

    @classmethod
    def create_empty(cls) -> Any:
        return cls(
            official=[],
            normal=Batch.create_empty(),
            timely=Batch.create_empty(),
            gauntlet=Batch.create_empty(),
            packs=[],
        )


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


class Part(dict):
    def __init__(
        self, stream: str = Union[bytes, str], default: Optional[Dict[str, Any]] = None
    ) -> None:
        self.parser = XMLParser()

        if isinstance(stream, str):
            stream = stream.encode()

        try:
            loaded = self.parser.load(stream)

        except Exception:
            if default is None:
                default = {}

            loaded = default

        super().__init__(loaded)

    def __str__(self) -> str:
        return dumps(self, indent=4)

    def __repr__(self) -> str:
        info = {"outer_len": len(self)}
        return make_repr(self, info)

    def copy(self) -> Any:
        return self.__class__(super().copy())

    def set(self, key: Any, value: Any) -> None:
        """Same as self[key] = value."""
        self[key] = value

    def dump(self) -> str:
        """Dump the part and return an xml string."""
        return self.parser.dump(self)


class Database:
    def __init__(self, main: str = "", levels: str = "") -> None:
        self.main = Part(main, get_default("main"))
        self.levels = Part(levels, get_default("levels"))

    def __repr__(self) -> str:
        info = {"main": repr(self.main), "levels": repr(self.levels)}
        return make_repr(self, info)

    def __json__(self) -> Dict[str, Any]:
        return {"main": self.main, "levels": self.levels}

    def get_user_name(self) -> str:
        return self.main.get("GJA_001", "unknown")

    def set_user_name(self, user_name: str) -> None:
        self.main.set("GJA_001", user_name)

    user_name = property(get_user_name, set_user_name)

    def get_password(self) -> str:
        return self.main.get("GJA_002", "unknown")

    def set_password(self, password: str) -> None:
        self.main.set("GJA_002", password)

    password = property(get_password, set_password)

    def get_account_id(self) -> int:
        return self.main.get("GJA_003", 0)

    def set_account_id(self, account_id: int) -> None:
        self.main.set("GJA_003", account_id)

    account_id = property(get_account_id, set_account_id)

    def get_user_id(self) -> int:
        return self.main.get("playerUserID", 0)

    def set_user_id(self, user_id: int) -> None:
        self.main.set("playerUserID", user_id)

    user_id = property(get_user_id, set_user_id)

    def get_udid(self) -> str:
        return self.main.get("playerUDID", "S0")

    def set_udid(self, udid: str) -> None:
        self.main.set("playerUDID", udid)

    udid = property(get_udid, set_udid)

    def get_bootups(self) -> int:
        return self.main.get("bootups", 0)

    def set_bootups(self, bootups: int) -> None:
        self.main.set("bootups", bootups)

    bootups = property(get_bootups, set_bootups)

    def get_followed(self) -> List[int]:
        return list(map(int, self.main.get("GLM_06", {}).keys()))

    def set_followed(self, followed: Sequence[int]) -> None:
        self.main.set("GLM_06", {str(account_id): 1 for account_id in followed})

    followed = property(get_followed, set_followed)

    def get_values(self) -> Values:  # O(nm), thanks rob
        values = Values.create_empty()
        prefixes = values.get_prefixes()

        for string in self.main.get("GS_completed", {}).keys():
            for prefix, array in prefixes.items():
                id_string = remove_prefix(string, prefix)

                if id_string != string:
                    array.append(int(id_string))
                    break

        return values

    def set_values(self, values: Values) -> None:
        mapping = {}
        prefixes = values.get_prefixes()

        for prefix, array in prefixes.items():
            mapping.update({f"{prefix}{value_id}": 1 for value_id in array})

        self.main.set("GS_completed", mapping)

    values = property(get_values, set_values)

    def _to_levels(self, level_dicts: List[Dict[str, Any]], dump_name: str) -> LevelCollection:
        return LevelCollection.launch(
            self,
            dump_name,
            map(LevelAPI.from_mapping, filter(lambda thing: isinstance(thing, dict), level_dicts)),
        )

    def load_saved_levels(self) -> LevelCollection:
        """Load "Saved Levels" into :class:`.api.LevelCollection`."""
        return self._to_levels(self.main.get("GLM_03", {}).values(), "dump_saved_levels")

    def dump_saved_levels(self, levels: LevelCollection) -> None:
        """Dump "Saved Levels" from :class:`.api.LevelCollection`."""
        self.main.set("GLM_03", {str(level.id): level.to_map() for level in levels})

    def load_my_levels(self) -> LevelCollection:
        """Load "My Levels" into :class:`.api.LevelCollection`."""
        return self._to_levels(self.levels.get("LLM_01", {}).values(), "dump_my_levels")

    def dump_my_levels(self, levels: LevelCollection, *, prefix: str = "k_") -> None:
        """Dump "My Levels" from :class:`.api.LevelCollection`."""
        stuff = {"_isArr": True}
        stuff.update({f"{prefix}{n}": level.to_map() for n, level in enumerate(levels)})

        self.levels.set("LLM_01", stuff)

    def dump(self) -> None:
        from gd.api.loader import save  # I hate circular imports. - nekit

        save.dump(self)

    def as_tuple(self) -> Tuple[Part, Part]:
        return (self.main, self.levels)


class LevelCollection(collections.UserList):
    def __init__(self, *args) -> None:
        if len(args) == 1:
            new_args = args[0]

            if iterable(new_args):
                args = new_args

        super().__init__(args)

        self._callback = None
        self._dump_name = None

    def get_by_name(self, name: str) -> Optional[LevelAPI]:
        return search.get(self, name=name)

    @classmethod
    def launch(cls, caller: Any, dump_name: str, iterable: Iterable) -> LevelCollection:
        self = cls(iterable)
        self._callback = caller
        self._dump_name = dump_name
        return self

    def dump(self, api: Optional[Database] = None) -> None:
        if api is None:
            api = self._callback

        getattr(api, self._dump_name)(self)


def iterable(maybe_iterable: Any) -> bool:
    try:
        iter(maybe_iterable)
        return True

    except TypeError:
        return False
