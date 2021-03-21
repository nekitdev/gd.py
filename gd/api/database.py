# DOCUMENT + REWRITE

from collections import UserList as ListDerive
from pathlib import Path

from attr import attrib, dataclass
from iters import iter

from gd.api.struct import LevelAPI  # type: ignore
from gd.iter_utils import extract_iterable_from_tuple
from gd.json import dumps
from gd.text_utils import make_repr, snake_to_camel
from gd.typing import Any, Dict, Iterable, List, Optional, Tuple, TypeVar, Union
from gd.xml_parser import XMLParser

__all__ = ("Part", "Database", "LevelStore", "LevelValues", "LevelCollection")

AnyString = Union[bytes, str]
PathLike = Union[str, Path]

IS_ARRAY = snake_to_camel("_is_arr")

MAIN = "CCGameManager.dat"
LEVELS = "CCLocalLevels.dat"

T = TypeVar("T")


def is_dict(some: Any) -> bool:
    return isinstance(some, dict)


@dataclass
class LevelStore:
    """Values that particular completed levels in the save."""

    completed: List[int] = attrib()
    stars: List[int] = attrib()
    demons: List[int] = attrib()

    @classmethod
    def create_empty(cls) -> "LevelStore":
        return cls(completed=[], stars=[], demons=[])


@dataclass
class LevelValues:
    """Values that represent completed levels in the save."""

    official: List[int] = attrib()
    normal: LevelStore = attrib()
    timely: LevelStore = attrib()
    gauntlet: LevelStore = attrib()
    packs: List[int] = attrib()

    def get_type_to_array(self) -> Dict[str, List[int]]:
        values, normal, timely, gauntlet = self, self.normal, self.timely, self.gauntlet

        return {
            "n": values.official,
            "c": normal.completed,
            "d": timely.completed,
            "g": gauntlet.completed,
            "star": normal.stars,
            "dstar": timely.stars,
            "gstar": gauntlet.stars,
            "demon": normal.demons,
            "ddemon": timely.demons,
            "gdemon": gauntlet.demons,
            "pack": values.packs,
        }

    def get_prefix_to_array(self) -> Dict[str, List[int]]:
        return {f"{type}_": array for type, array in self.get_type_to_array().items()}

    @classmethod
    def create_empty(cls) -> "LevelValues":
        return cls(
            official=[],
            normal=LevelStore.create_empty(),
            timely=LevelStore.create_empty(),
            gauntlet=LevelStore.create_empty(),
            packs=[],
        )


def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]

    return string


class Part(dict):
    @classmethod
    def load(cls, stream: AnyString, default: Optional[Dict[str, T]] = None) -> "Part":
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
        info = {"length": len(self)}

        return make_repr(self, info)

    def copy(self) -> "Part":
        return self.__class__(super().copy())

    def set(self, key: str, value: T) -> None:
        """Same as self[key] = value."""
        self[key] = value

    def dump_as_bytes(self) -> bytes:
        """Dump the part and return xml data."""
        return self.parser.dump_as_bytes(self)

    def dump(self) -> str:
        """Dump the part and return xml string."""
        return self.parser.dump(self)


class Database:
    def __init__(
        self, main: Optional[AnyString] = None, levels: Optional[AnyString] = None
    ) -> None:
        self.main = Part.load(main) if main else Part()
        self.levels = Part.load(levels) if levels else Part()

    def __repr__(self) -> str:
        info = {"main": repr(self.main), "levels": repr(self.levels)}

        return make_repr(self, info)

    def __json__(self) -> Dict[str, Part]:
        return {"main": self.main, "levels": self.levels}

    def __bool__(self) -> bool:
        if self.main:
            return True

        if self.levels:
            return True

        return False

    def is_empty(self) -> bool:
        """Check if the database is empty."""
        return not self

    def get_user_name(self) -> str:
        """Player name."""
        return self.main.get("GJA_001", "unknown")

    def set_user_name(self, user_name: str) -> None:
        """Set player name to ``user_name``."""
        self.main.set("GJA_001", user_name)

    user_name = property(get_user_name, set_user_name)

    def get_password(self) -> str:
        """Player password."""
        return self.main.get("GJA_002", "unknown")

    def set_password(self, password: str) -> None:
        """Set player password to ``password``."""
        self.main.set("GJA_002", password)

    password = property(get_password, set_password)

    def get_account_id(self) -> int:
        """Player Account ID, same as ``account_id`` of users."""
        return self.main.get("GJA_003", 0)

    def set_account_id(self, account_id: int) -> None:
        """Set player Account ID to ``account_id``."""
        self.main.set("GJA_003", account_id)

    account_id = property(get_account_id, set_account_id)

    def get_user_id(self) -> int:
        """Player User ID, same as ``id`` of users."""
        return self.main.get("playerUserID", 0)

    def set_user_id(self, user_id: int) -> None:
        """Set player User ID to ``user_id``."""
        self.main.set("playerUserID", user_id)

    user_id = property(get_user_id, set_user_id)

    def get_udid(self) -> str:
        """Player UDID."""
        return self.main.get("playerUDID", "S0")

    def set_udid(self, udid: str) -> None:
        """Set player UDID to ``user_id``."""
        self.main.set("playerUDID", udid)

    udid = property(get_udid, set_udid)

    def get_bootups(self) -> int:
        """Count of game bootups."""
        return self.main.get("bootups", 0)

    def set_bootups(self, bootups: int) -> None:
        """Set bootups to ``bootups``."""
        self.main.set("bootups", bootups)

    bootups = property(get_bootups, set_bootups)

    def get_followed(self) -> List[int]:
        """List of followed users."""
        return list(map(int, self.main.get("GLM_06", {}).keys()))

    def set_followed(self, followed: Iterable[int]) -> None:
        """Set followed users to ``followed``."""
        self.main.set("GLM_06", {str(account_id): 1 for account_id in followed})

    followed = property(get_followed, set_followed)

    def get_values(self) -> LevelValues:  # O(nm), thanks rob
        """:class:`~gd.api.database.LevelValues` that represent completed levels."""
        values = LevelValues.create_empty()
        prefix_to_array = values.get_prefix_to_array()

        for string in self.main.get("GS_completed", {}).keys():
            for prefix, array in prefix_to_array.items():
                id_string = remove_prefix(string, prefix)

                if id_string != string:
                    array.append(int(id_string))
                    break

        return values

    def set_values(self, values: LevelValues) -> None:
        """Set :class:`~gd.api.database.LevelValues` to ``values``."""
        mapping = {}
        prefix_to_array = values.get_prefix_to_array()

        for prefix, array in prefix_to_array.items():
            mapping.update({f"{prefix}{value_id}": 1 for value_id in array})

        self.main.set("GS_completed", mapping)

    values = property(get_values, set_values)

    def to_levels(self, raw_levels: Iterable[Dict[str, T]], function: str) -> "LevelCollection":
        return LevelCollection.launch(
            self, function, map(LevelAPI.from_data, filter(is_dict, raw_levels))
        )

    def load_saved_levels(self) -> "LevelCollection":
        """Load saved levels into :class:`~gd.api.LevelCollection`."""
        return self.to_levels(self.main.get("GLM_03", {}).values(), "dump_saved_levels")

    get_saved_levels = load_saved_levels

    def dump_saved_levels(self, levels: "LevelCollection") -> None:
        """Dump saved levels from :class:`~gd.api.LevelCollection`."""
        self.main.set("GLM_03", {str(level.id): level.to_data() for level in levels})

    set_saved_levels = dump_saved_levels

    saved_levels = property(get_saved_levels, set_saved_levels)

    def load_created_levels(self) -> "LevelCollection":
        """Load created levels into :class:`~gd.api.LevelCollection`."""
        return self.to_levels(self.levels.get("LLM_01", {}).values(), "dump_created_levels")

    get_created_levels = load_created_levels

    def dump_created_levels(self, levels: "LevelCollection") -> None:
        """Dump created levels from :class:`~gd.api.LevelCollection`."""
        store = {IS_ARRAY: True}

        store.update({f"k_{index}": level.to_data() for index, level in enumerate(levels)})

        self.levels.set("LLM_01", store)

    set_created_levels = dump_created_levels

    created_levels = property(get_created_levels, set_created_levels)

    @classmethod
    def load(
        cls,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> "Database":
        """Load the database. See :meth:`~gd.api.SaveUtils.load` for more."""
        from gd.api.loader import save  # ...

        return save.load(main=main, levels=levels, main_file=main_file, levels_file=levels_file)

    def dump(
        self,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> None:
        """Dump the database back. See :meth:`~gd.api.SaveUtils.dump` for more."""
        from gd.api.loader import save  # I hate circular imports.

        save.dump(
            self, main=main, levels=levels, main_file=main_file, levels_file=levels_file
        )

    def as_tuple(self) -> Tuple[Part, Part]:
        return (self.main, self.levels)


class LevelCollection(ListDerive):
    """Collection of :class:`~gd.api.LevelAPI` objects."""

    def __init__(self, *args) -> None:
        super().__init__(extract_iterable_from_tuple(args))  # type: ignore

        self._callback: Optional[Database] = None
        self._function: Optional[str] = None

    def get_by_name(self, name: str) -> Optional[LevelAPI]:
        """Fetch a level by ``name``. Returns ``None`` if not found."""
        return iter(self).get(name=name)

    @classmethod
    def launch(cls, callback: Database, function: str, iterable: Iterable[T]) -> "LevelCollection":
        self = cls(iterable)

        self._callback = callback
        self._function = function

        return self

    def dump(self, database: Optional[Database] = None) -> None:
        """Dump levels to ``database``, if provided.
        Otherwise, try to dump back to the database that created this collection.
        """
        if database is None:
            database = self._callback  # type: ignore

        getattr(database, self._function)(self)  # type: ignore
