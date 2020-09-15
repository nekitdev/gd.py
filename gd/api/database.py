from collections import UserList
from pathlib import Path

from attr import attrib, dataclass

from gd.json import dumps
from gd.search_utils import get
from gd.text_utils import make_repr
from gd.typing import AnyStr, Dict, Iterable, List, Optional, Tuple, TypeVar, Union
from gd.xml_parser import XMLParser

from gd.api.struct import LevelAPI  # type: ignore
from gd.api.utils import MAIN_DEFAULTS, LEVELS_DEFAULTS

__all__ = ("Part", "Database", "LevelCollection")

PathLike = Union[str, Path]

MAIN = "CCGameManager.dat"
LEVELS = "CCLocalLevels.dat"

T = TypeVar("T")


@dataclass
class Batch:
    completed: List[int] = attrib()
    stars: List[int] = attrib()
    demons: List[int] = attrib()

    @classmethod
    def create_empty(cls) -> "Batch":
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
    def create_empty(cls) -> "Values":
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


def is_dict(some: T) -> bool:
    return isinstance(some, dict)


class Part(dict):
    @classmethod
    def new(cls, stream: AnyStr, default: Optional[Dict[str, T]] = None) -> "Part":
        self = cls()

        try:
            self.update(self.parser.load(stream))

        except Exception:
            if default is None:
                default = {}

            self.update(default)

        return self

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parser = XMLParser()

    def __str__(self) -> str:
        return dumps(self, indent=4)

    def __repr__(self) -> str:
        info = {"outer_len": len(self)}
        return make_repr(self, info)

    def copy(self) -> "Part":
        return self.__class__(super().copy())

    def set(self, key: str, value: T) -> None:
        """Same as self[key] = value."""
        self[key] = value

    def dump(self) -> bytes:
        """Dump the part and return xml data."""
        return self.parser.dump(self)

    def dump_string(self) -> str:
        """Dump the part and return xml string."""
        return self.parser.dump_string(self)


class Database:
    def __init__(self, main: Optional[AnyStr] = None, levels: Optional[AnyStr] = None) -> None:
        self.main = Part.new(main, MAIN_DEFAULTS) if main else Part(MAIN_DEFAULTS)
        self.levels = Part.new(levels, LEVELS_DEFAULTS) if levels else Part(LEVELS_DEFAULTS)

    def __repr__(self) -> str:
        info = {"main": repr(self.main), "levels": repr(self.levels)}
        return make_repr(self, info)

    def __json__(self) -> Dict[str, Part]:
        return {"main": self.main, "levels": self.levels}

    def is_empty(self) -> bool:
        return self.main == MAIN_DEFAULTS and self.levels == LEVELS_DEFAULTS

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

    def set_followed(self, followed: Iterable[int]) -> None:
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

    def to_levels(self, level_dicts: Iterable[Dict[str, T]], func_name: str) -> "LevelCollection":
        return LevelCollection.launch(
            self, func_name, map(LevelAPI.from_data, filter(is_dict, level_dicts))
        )

    def load_saved_levels(self) -> "LevelCollection":
        """Load "Saved Levels" into :class:`.api.LevelCollection`."""
        return self.to_levels(self.main.get("GLM_03", {}).values(), "dump_saved_levels")

    def dump_saved_levels(self, levels: "LevelCollection") -> None:
        """Dump "Saved Levels" from :class:`.api.LevelCollection`."""
        self.main.set("GLM_03", {str(level.id): level.to_data() for level in levels})

    def load_my_levels(self) -> "LevelCollection":
        """Load "My Levels" into :class:`.api.LevelCollection`."""
        return self.to_levels(self.levels.get("LLM_01", {}).values(), "dump_my_levels")

    def dump_my_levels(self, levels: "LevelCollection", *, prefix: str = "k_") -> None:
        """Dump "My Levels" from :class:`.api.LevelCollection`."""
        store = {"_isArr": True}

        store.update({f"{prefix}{index}": level.to_data() for index, level in enumerate(levels)})

        self.levels.set("LLM_01", store)

    @classmethod
    def load(
        cls,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> "Database":
        from gd.api.loader import save  # ...

        return save.load(main=main, levels=levels, main_file=main_file, levels_file=levels_file)

    def dump(
        self,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> None:
        from gd.api.loader import save  # I hate circular imports.

        save.dump(db=self, main=main, levels=levels, main_file=main_file, levels_file=levels_file)

    def as_tuple(self) -> Tuple[Part, Part]:
        return (self.main, self.levels)


class LevelCollection(UserList):
    def __init__(self, *args) -> None:
        if len(args) == 1:
            maybe_args = args[0]

            if is_iterable(maybe_args):
                args = maybe_args

        super().__init__(args)

        self._callback: Optional[Database] = None
        self._funcname: Optional[str] = None

    def get_by_name(self, name: str) -> Optional[LevelAPI]:
        return get(self, name=name)

    @classmethod
    def launch(cls, callback: Database, funcname: str, iterable: Iterable[T]) -> "LevelCollection":
        self = cls(iterable)

        self._callback = callback
        self._funcname = funcname

        return self

    def dump(self, database: Optional[Database] = None) -> None:
        if database is None:
            database = self._callback  # type: ignore

        getattr(database, self._funcname)(self)  # type: ignore


def is_iterable(maybe_iterable: Union[Iterable[T], T]) -> bool:
    try:
        iter(maybe_iterable)  # type: ignore
        return True

    except TypeError:
        return False
