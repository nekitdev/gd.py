from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Optional, Type, TypeVar

from attrs import define, field
from iters.async_iters import wrap_async_iter
from typing_aliases import DynamicTuple

from gd.color import Color
from gd.constants import (
    DEFAULT_COINS,
    DEFAULT_ID,
    DEFAULT_STARS,
    EMPTY,
    UNKNOWN,
)
from gd.entity import Entity
from gd.enums import Difficulty, GauntletID
from gd.filters import Filters
from gd.models import GauntletModel, MapPackModel

if TYPE_CHECKING:
    from gd.client import Client
    from gd.level import Level

__all__ = ("LevelPack", "Gauntlet", "MapPack")

LP = TypeVar("LP", bound="LevelPack")


@define()
class LevelPack(Entity):
    name: str = field(eq=False)
    level_ids: DynamicTuple[int] = field(default=(), eq=False)
    levels: DynamicTuple[Level] = field(default=(), eq=False, init=False)

    @classmethod
    def default(cls: Type[LP], id: int = DEFAULT_ID) -> LP:
        return cls(id=id, name=EMPTY)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return self.name or UNKNOWN

    @wrap_async_iter
    async def get_levels(self) -> AsyncIterator[Level]:
        levels = await self.client.search_levels_on_page(
            query=self.level_ids, filters=Filters.search_many()
        ).tuple()

        self.levels = levels

        for level in levels:
            yield level

    def attach_client_unchecked(self: LP, client: Optional[Client]) -> LP:
        for level in self.levels:
            level.attach_client_unchecked(client)

        return super().attach_client_unchecked(client)

    def attach_client(self: LP, client: Client) -> LP:
        for level in self.levels:
            level.attach_client(client)

        return super().attach_client(client)

    def detach_client(self: LP) -> LP:
        for level in self.levels:
            level.detach_client()

        return super().detach_client()


G = TypeVar("G", bound="Gauntlet")


@define()
class Gauntlet(LevelPack):
    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @classmethod
    def from_model(cls: Type[G], model: GauntletModel) -> G:
        id = model.id

        return cls(id=id, name=GauntletID(id).name.title(), level_ids=model.level_ids)


MP = TypeVar("MP", bound="MapPack")


@define()
class MapPack(LevelPack):
    stars: int = field(default=DEFAULT_STARS, eq=False)
    coins: int = field(default=DEFAULT_COINS, eq=False)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT, eq=False)
    color: Color = field(factory=Color.default, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    @property
    def colored_name(self) -> str:
        return self.color.paint(self.name)

    @classmethod
    def from_model(cls: Type[MP], model: MapPackModel) -> MP:
        return cls(
            id=model.id,
            name=model.name,
            level_ids=model.level_ids,
            stars=model.stars,
            coins=model.coins,
            difficulty=model.difficulty,
            color=model.color,
        )
