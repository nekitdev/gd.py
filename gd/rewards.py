from __future__ import annotations

from typing import Type, TypeVar

from attrs import define, field
from pendulum import DateTime, Duration
from pendulum import duration as duration_factory

from gd.constants import (
    DEFAULT_AMOUNT,
    DEFAULT_CHEST_COUNT,
    DEFAULT_DIAMONDS,
    DEFAULT_KEYS,
    DEFAULT_ORBS,
    DEFAULT_REWARD,
    EMPTY,
    UNKNOWN,
)
from gd.date_time import utc_now
from gd.entity import Entity
from gd.enums import QuestType, ShardType
from gd.models import ChestModel, QuestModel
from gd.string_utils import case_fold, tick

__all__ = ("Chest", "Quest")

CHEST = "Chest; orbs: {}, diamonds: {}, keys: {}, shard: {}, new in {}"

C = TypeVar("C", bound="Chest")


@define()
class Chest(Entity):
    orbs: int = field(default=DEFAULT_ORBS, eq=False)
    diamonds: int = field(default=DEFAULT_DIAMONDS, eq=False)
    shard_type: ShardType = field(default=ShardType.DEFAULT, eq=False)
    keys: int = field(default=DEFAULT_KEYS, eq=False)
    count: int = field(default=DEFAULT_CHEST_COUNT, eq=False)

    duration: Duration = field(factory=duration_factory, eq=False)

    created_at: DateTime = field(factory=utc_now, init=False, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        return CHEST.format(
            self.orbs, self.diamonds, self.keys, case_fold(self.shard_type.name), self.duration
        )

    @classmethod
    def from_model(cls: Type[C], model: ChestModel, id: int, count: int, duration: Duration) -> C:
        return cls(
            id=id,
            orbs=model.orbs,
            diamonds=model.diamonds,
            shard_type=model.shard_type,
            keys=model.keys,
            count=count,
            duration=duration,
        )

    @property
    def ready_at(self) -> DateTime:
        return self.created_at + self.duration  # type: ignore


QUEST_UNKNOWN = "Quest {}; reward: {}, new in {}"
QUEST = "Quest {}; collect: {} {}, reward: {}, new in {}"


Q = TypeVar("Q", bound="Quest")


@define()
class Quest(Entity):
    name: str = field(default=EMPTY, eq=False)
    type: QuestType = field(default=QuestType.DEFAULT, eq=False)
    amount: int = field(default=DEFAULT_AMOUNT, eq=False)
    reward: int = field(default=DEFAULT_REWARD, eq=False)

    duration: Duration = field(factory=duration_factory, eq=False)

    created_at: DateTime = field(factory=utc_now, eq=False)

    def __hash__(self) -> int:
        return hash(type(self)) ^ self.id

    def __str__(self) -> str:
        if self.type.is_unknown():
            return QUEST_UNKNOWN.format(tick(self.name or UNKNOWN), self.reward, self.duration)

        return QUEST.format(
            tick(self.name or UNKNOWN),
            self.amount,
            case_fold(self.type.name),
            self.reward,
            self.duration,
        )

    @classmethod
    def from_model(cls: Type[Q], model: QuestModel, duration: Duration) -> Q:
        return cls(
            id=model.id,
            name=model.name,
            type=model.type,
            amount=model.amount,
            reward=model.reward,
            duration=duration,
        )

    @property
    def new_at(self) -> DateTime:
        return self.created_at + self.duration  # type: ignore
