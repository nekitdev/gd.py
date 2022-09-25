from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Optional, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter

from gd.color import Color
from gd.constants import DEFAULT_COINS, DEFAULT_STARS
from gd.entity import Entity
from gd.enums import Difficulty
from gd.filters import Filters
from gd.typing import DynamicTuple

if TYPE_CHECKING:
    from gd.client import Client

__all__ = ("Gauntlet", "MapPack")

if TYPE_CHECKING:
    from gd.level import Level


G = TypeVar("G", bound="Gauntlet")


@define()
class Gauntlet(Entity):
    name: str = field(eq=False)
    level_ids: DynamicTuple[int] = field(eq=False)
    _levels: DynamicTuple[Level] = field(default=(), repr=False, init=False, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

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

    def maybe_attach_client(self: G, client: Optional[Client]) -> G:
        for level in self.levels:
            level.maybe_attach_client(client)

        return super().maybe_attach_client(client)

    def attach_client(self: G, client: Client) -> G:
        for level in self.levels:
            level.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: G) -> G:
        for level in self.levels:
            level.detach_client()

        return super().detach_client()


@define()
class MapPack(Gauntlet):
    stars: int = field(default=DEFAULT_STARS, eq=False)
    coins: int = field(default=DEFAULT_COINS, eq=False)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT, eq=False)
    primary_color: Color = field(factory=Color.default, eq=False)
    secondary_color: Color = field(factory=Color.default, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id
