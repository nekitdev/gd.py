from gd.typing import Any, Client, Dict, Gauntlet, Level, List, MapPack, Tuple

from gd.abstractentity import AbstractEntity
from gd.colors import Color

from gd.utils.converter import Converter
from gd.utils.enums import LevelDifficulty
from gd.utils.filters import Filters
from gd.utils.indexer import Index
from gd.utils.parser import ExtDict
from gd.utils.text_tools import make_repr


class Gauntlet(AbstractEntity):
    """Class that represents *The Lost Gauntlet* in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """

    def __init__(self, **options) -> None:
        super().__init__(**options)
        self._levels = ()

    def __repr__(self) -> str:
        info = {"id": self.id, "name": self.name, "levels": self.level_ids}

        if self.levels:
            info.update(levels=self.levels)

        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    @classmethod
    def from_data(cls, data: ExtDict, client: Client) -> Gauntlet:
        try:
            level_ids = tuple(map(int, data.get(Index.GAUNTLET_LEVEL_IDS, "").split(",")))
        except ValueError:
            level_ids = ()

        gid = data.getcast(Index.GAUNTLET_ID, 0, int)
        name = Converter.get_gauntlet_name(gid)

        return cls(id=gid, name=name, level_ids=level_ids, client=client)

    def __json__(self) -> Dict[str, Any]:
        return dict(super().__json__(), levels=self.levels)

    @property
    def name(self) -> str:
        """:class:`str`: Name of the Gauntlet."""
        return self.options.get("name", "Unknown")

    @property
    def level_ids(self) -> Tuple[int]:
        """Tuple[:class:`int`]: Tuple of level IDs that are contained in the gauntlet."""
        return self.options.get("level_ids", ())

    @property
    def levels(self) -> Tuple[Level]:
        """Tuple[:class:`.Level`]: Tuple containing levels of the Gauntlet.

        Can be retrieved with :meth:`.Gauntlet.get_levels`.
        """
        return self._levels

    async def get_levels(self) -> List[Level]:
        """|coro|

        Retrieves levels of a Gauntlet or its subclass.

        Returns
        -------
        List[:class:`.Level`]
            List of levels that are found.
        """
        filters, query = Filters.setup_search_many(), ",".join(map(str, self.level_ids))

        levels = await self.client.search_levels_on_page(query=query, filters=filters)

        self._levels = tuple(levels)
        return levels


class MapPack(Gauntlet):
    """Class that represents *Map Pack* in Geometry Dash.
    This class is derived from :class:`.Gauntlet`.
    """

    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.options = options

    def __repr__(self) -> str:
        info = {"id": self.id, "name": self.name, "color": self.color, "levels": self.level_ids}

        if self.levels:
            info.update(levels=self.levels)

        return make_repr(self, info)

    @classmethod
    def from_data(cls, data: ExtDict, client: Client) -> MapPack:
        try:
            level_ids = tuple(map(int, data.get(Index.MAP_PACK_LEVEL_IDS, "").split(",")))
        except ValueError:
            level_ids = ()

        color_string = data.get(Index.MAP_PACK_COLOR, "255,255,255")
        color = Color.from_rgb(*map(int, color_string.split(",")))

        difficulty = Converter.value_to_pack_difficulty(
            data.getcast(Index.MAP_PACK_DIFFICULTY, 0, int)
        )

        return cls(
            id=data.getcast(Index.MAP_PACK_ID, 0, int),
            name=data.get(Index.MAP_PACK_NAME, "unknown"),
            level_ids=level_ids,
            stars=data.getcast(Index.MAP_PACK_STARS, 0, int),
            coins=data.getcast(Index.MAP_PACK_COINS, 0, int),
            difficulty=difficulty,
            color=color,
            client=client,
        )

    @property
    def stars(self) -> int:
        """:class:`int`: Amount of stars this map pack has."""
        return self.options.get("stars", 0)

    @property
    def coins(self) -> int:
        """:class:`int`: Number of coins this map pack grants on completion."""
        return self.options.get("coins", 0)

    @property
    def difficulty(self) -> LevelDifficulty:
        """:class:`.LevelDifficulty`: Average difficulty of a map pack."""
        return LevelDifficulty.from_value(self.options.get("difficulty", -1))

    @property
    def color(self) -> Color:
        """:class:`.Color`: Color of a map pack."""
        return self.options.get("color", Color(0xFFFFFF))
