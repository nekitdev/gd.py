from __future__ import annotations

from datetime import datetime, timedelta

from attrs import define, field

from gd.constants import UNKNOWN
from gd.entity import Entity
from gd.enums import QuestType, ShardType

# from gd.models import ChestModel, QuestModel
from gd.string_utils import case_fold, tick

# from typing import TYPE_CHECKING


# if TYPE_CHECKING:
#     from gd.client import Client

__all__ = ("Chest", "Quest")


CHEST = "Chest; orbs: {}, diamonds: {}, keys: {}, shard: {}, new in {}"


@define()
class Chest(Entity):
    orbs: int = field(default=0)
    diamonds: int = field(default=0)
    shard_type: ShardType = field(default=ShardType.UNKNOWN)
    keys: int = field(default=0)
    count: int = field(default=0)

    delta: timedelta = field(factory=timedelta)

    _created_at: datetime = field(factory=datetime.utcnow, init=False, repr=False)

    def __str__(self) -> str:
        return CHEST.format(
            self.orbs, self.diamonds, self.keys, case_fold(self.shard_type.name), self.delta
        )

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def ready_at(self) -> datetime:
        return self.created_at + self.delta


QUEST_UNKNOWN = "Quest {}; reward: {}, new in {}"
QUEST = "Quest {}; collect: {} {}, reward: {}, new in {}"


@define()
class Quest(Entity):
    name: str = field(default=UNKNOWN)
    type: QuestType = field(default=QuestType.UNKNOWN)
    amount: int = field(default=0)
    reward: int = field(default=0)

    delta: timedelta = field(factory=timedelta)

    _created_at: datetime = field(factory=datetime.utcnow, init=False, repr=False)

    def __str__(self) -> str:
        if self.type is QuestType.UNKNOWN:
            return QUEST_UNKNOWN.format(tick(self.name), self.reward, self.delta)

        return QUEST.format(
            tick(self.name), self.amount, case_fold(self.type.name), self.reward, self.delta
        )

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def new_at(self) -> datetime:
        return self.created_at + self.delta
