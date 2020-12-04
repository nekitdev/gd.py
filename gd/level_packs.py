from gd.abstract_entity import AbstractEntity
from gd.async_iter import async_iterable
from gd.color import Color
from gd.enums import GauntletID, LevelDifficulty
from gd.filters import Filters
from gd.model import GauntletModel, MapPackModel  # type: ignore
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, Tuple

__all__ = ("Gauntlet", "MapPack")

if TYPE_CHECKING:
    from gd.client import Client  # noqa
    from gd.level import Level  # noqa


class Gauntlet(AbstractEntity):
    """Class that represents *The Lost Gauntlet* in Geometry Dash.
    This class is derived from :class:`~gd.AbstractEntity`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)

            Return name of the gauntlet.

        .. describe:: repr(x)

            Return representation of the gauntlet, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    def __repr__(self) -> str:
        info = {
            "id": self.id,
            "name": self.name,
            "levels": self.levels if self.levels else self.level_ids,
        }

        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()

        result.update(levels=self.levels)

        return result

    @classmethod
    def from_model(  # type: ignore
        cls, model: GauntletModel, *, client: Optional["Client"] = None
    ) -> "Gauntlet":
        gauntlet_id = GauntletID.from_value(model.id, GauntletID.UNKNOWN)
        name = f"{gauntlet_id.title} Gauntlet"

        return cls(id=model.id, name=name, level_ids=model.levels, client=client)

    @property
    def name(self) -> str:
        """:class:`str`: Name of the Gauntlet."""
        return self.options.get("name", "Unknown")

    @property
    def level_ids(self) -> Tuple[int]:
        """Tuple[:class:`int`]: Tuple of level IDs that are contained in the gauntlet."""
        return self.options.get("level_ids", ())

    @property
    def levels(self) -> Tuple["Level"]:
        """Tuple[:class:`~gd.Level`]: Tuple containing levels of the Gauntlet.

        Can be retrieved with :meth:`~gd.Gauntlet.get_levels`.
        """
        return self.options.get("levels", ())

    @async_iterable
    async def get_levels(self) -> AsyncIterator["Level"]:
        """Retrieves levels of a Level Pack. Also updates inner ``levels`` attribute.

        Returns
        -------
        AsyncIterator[:class:`~gd.Level`]
            Levels that are found.
        """
        levels: List["Level"] = await self.client.search_levels_on_page(
            query=self.level_ids, filters=Filters.search_many()
        ).list()

        self.options.update(levels=tuple(levels))

        for level in levels:
            yield level


class MapPack(Gauntlet):
    """Class that represents *Map Pack* in Geometry Dash.
    This class is derived from :class:`~gd.Gauntlet`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)

            Return name of the map pack.

        .. describe:: repr(x)

            Return representation of the map pack, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    def __repr__(self) -> str:
        info = {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "other_color": self.other_color,
            "levels": self.levels if self.levels else self.level_ids,
        }

        return make_repr(self, info)

    @classmethod
    def from_model(  # type: ignore
        cls, model: MapPackModel, *, client: Optional["Client"] = None
    ) -> "MapPack":
        return cls(
            id=model.id,
            name=model.name,
            level_ids=model.levels,
            stars=model.stars,
            coins=model.coins,
            difficulty=model.difficulty,
            color=model.color,
            other_color=model.other_color,
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
        """:class:`~gd.LevelDifficulty`: Average difficulty of a map pack."""
        return LevelDifficulty.from_value(self.options.get("difficulty", -1))

    @property
    def color(self) -> Color:
        """:class:`~gd.Color`: Color of a map pack."""
        return self.options.get("color", Color(0xFFFFFF))

    @property
    def other_color(self) -> Color:
        """:class:`~gd.Color`: Other color of a map pack."""
        return self.options.get("other_color", Color(0xFFFFFF))
