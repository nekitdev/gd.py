from .typing import Level, List, Tuple

from .abstractentity import AbstractEntity
from .colors import Color

from .utils.enums import LevelDifficulty
from .utils.filters import Filters
from .utils.text_tools import make_repr


class Gauntlet(AbstractEntity):
    """Class that represents *The Lost Gauntlet* in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self._levels = ()

    def __repr__(self) -> str:
        info = {
            'id': self.id,
            'name': self.name,
            'levels': self.level_ids
        }

        if self.levels:
            info.update(levels=self.levels)

        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    def _json(self) -> dict:
        final = dict(levels=self.levels)
        final.update(super()._json())
        return final

    @property
    def name(self) -> str:
        """:class:`str`: Name of the Gauntlet."""
        return self.options.get('name', 'Unknown')

    @property
    def level_ids(self) -> Tuple[int]:
        """Tuple[:class:`int`]: Tuple of level IDs that are contained in the gauntlet."""
        return self.options.get('level_ids', ())

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
        filters, query = Filters.setup_search_many(), ','.join(map(str, self.level_ids))

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
        info = {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'levels': self.level_ids
        }

        if self.levels:
            info.update(levels=self.levels)

        return make_repr(self, info)

    @property
    def stars(self) -> int:
        """:class:`int`: Amount of stars this map pack has."""
        return self.options.get('stars', 0)

    @property
    def coins(self) -> int:
        """:class:`int`: Number of coins this map pack grants on completion."""
        return self.options.get('coins', 0)

    @property
    def difficulty(self) -> LevelDifficulty:
        """:class:`.LevelDifficulty`: Average difficulty of a map pack."""
        return LevelDifficulty.from_value(self.options.get('difficulty', -1))

    @property
    def color(self) -> Color:
        """:class:`.Color`: Color of a map pack."""
        return self.options.get('color', Color(0xffffff))
