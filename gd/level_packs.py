from .abstractentity import AbstractEntity
from .colors import Colour

from .utils.enums import LevelDifficulty
from .utils.filters import Filters
from .utils.wrap_tools import make_repr

class Gauntlet(AbstractEntity):
    """Class that represents *The Lost Gauntlet* in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
        self._levels = ()

    def __repr__(self):
        info = {
            'id': self.id,
            'name': self.name,
            'levels': self.level_ids
        }

        if self.levels:
            info.update({'levels': self.levels})

        return make_repr(self, info)

    @property
    def name(self):
        """:class:`str`: Name of the Gauntlet."""
        return self.options.get('name', 'Unknown')

    @property
    def level_ids(self):
        """Tuple[:class:`int`]: Tuple of level IDs that are contained in the gauntlet."""
        return self.options.get('level_ids', ())

    @property
    def levels(self):
        """Tuple[:class:`.Level`]: Tuple containing levels of the Gauntlet.

        Can be retrieved with :meth:`.Gauntlet.get_levels`.
        """
        return self._levels

    async def get_levels(self):
        """|coro|

        Retrieves levels of a Gauntlet or its subclass.

        Returns
        -------
        List[:class:`.Level`]
            List of levels that are found.
        """
        filters, query = Filters.setup_search_many(), ','.join(map(str, self.level_ids))

        levels = await self._client.search_levels_on_page(query=query, filters=filters)

        self._levels = tuple(levels)
        return levels


class MapPack(Gauntlet):
    """Class that represents *Map Pack* in Geometry Dash.
    This class is derived from :class:`.Gauntlet`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    def __repr__(self):
        info = {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'levels': self.level_ids
        }

        if self.levels:
            info.update({'levels': self.levels})

        return make_repr(self, info)

    @property
    def stars(self):
        """:class:`int`: Amount of stars this map pack has."""
        return self.options.get('stars', 0)

    @property
    def coins(self):
        """:class:`int`: Number of coins this map pack grants on completion."""
        return self.options.get('coins', 0)

    @property
    def difficulty(self):
        """:class:`.LevelDifficulty`: Average difficulty of a map pack."""
        return self.options.get('difficulty', LevelDifficulty(-1))

    @property
    def color(self):
        """:class:`.Colour`: Colour of a map pack."""
        return self.options.get('color', Colour(0xffffff))
