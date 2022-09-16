from __future__ import annotations

from datetime import datetime, timedelta

from attrs import define, field

from gd.constants import DEFAULT_CHEST_COUNT, DEFAULT_DIAMONDS, DEFAULT_KEYS, DEFAULT_ORBS, UNKNOWN
from gd.entity import Entity
from gd.enums import QuestType, ShardType

# from gd.models import ChestModel, QuestModel
from gd.string_utils import case_fold, tick

__all__ = ("Chest", "Quest")


CHEST = "Chest; orbs: {}, diamonds: {}, keys: {}, shard: {}, new in {}"


@define()
class Chest(Entity):
    orbs: int = field(default=DEFAULT_ORBS, eq=False)
    diamonds: int = field(default=DEFAULT_DIAMONDS, eq=False)
    shard_type: ShardType = field(default=ShardType.UNKNOWN, eq=False)
    keys: int = field(default=DEFAULT_KEYS, eq=False)
    count: int = field(default=DEFAULT_CHEST_COUNT, eq=False)

    delta: timedelta = field(factory=timedelta, eq=False)

    created_at: datetime = field(factory=datetime.utcnow, init=False, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return CHEST.format(
            self.orbs, self.diamonds, self.keys, case_fold(self.shard_type.name), self.delta
        )

    @property
    def ready_at(self) -> datetime:
        return self.created_at + self.delta


QUEST_UNKNOWN = "Quest {}; reward: {}, new in {}"
QUEST = "Quest {}; collect: {} {}, reward: {}, new in {}"


@define()
class Quest(Entity):
    name: str = field(default=UNKNOWN, eq=False)
    type: QuestType = field(default=QuestType.UNKNOWN, eq=False)
    amount: int = field(default=0, eq=False)
    reward: int = field(default=0, eq=False)

    delta: timedelta = field(factory=timedelta, eq=False)

    created_at: datetime = field(factory=datetime.utcnow, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        if self.type is QuestType.UNKNOWN:
            return QUEST_UNKNOWN.format(tick(self.name), self.reward, self.delta)

        return QUEST.format(
            tick(self.name), self.amount, case_fold(self.type.name), self.reward, self.delta
        )

    @property
    def new_at(self) -> datetime:
        return self.created_at + self.delta
