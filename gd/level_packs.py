from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

from attrs import define, field
from iters.async_iters import wrap_async_iter

from gd.color import Color
from gd.entity import Entity

# from gd.enums import Difficulty, GauntletID
from gd.filters import Filters

# from gd.model import GauntletModel, MapPackModel
from gd.typing import DynamicTuple

__all__ = ("Gauntlet", "MapPack")

if TYPE_CHECKING:
    from gd.client import Client  # noqa
    from gd.level import Level  # noqa


@define()
class Gauntlet(Entity):
    name: str = field()
    level_ids: DynamicTuple[int] = field()
    _levels: DynamicTuple[Level] = field(default=(), repr=False, init=False)

    def __str__(self) -> str:
        return self.name

    @property
    def levels(self) -> DynamicTuple[Level]:
        return self._levels

    @wrap_async_iter
    async def get_levels(self) -> AsyncIterator[Level]:
        levels = await self.client.search_levels_on_page(
            query=self.level_ids, filters=Filters.search_many()
        ).tuple()

        self._levels = levels

        for level in levels:
            yield level


@define()
class MapPack(Gauntlet):
    stars: int
    coins: int
    # difficulty: Difficulty
    primary_color: Color
    secondary_color: Color
