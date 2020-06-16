from datetime import datetime, timedelta

from gd.abstractentity import AbstractEntity

from gd.utils.enums import ShardType, QuestType
from gd.utils.text_tools import make_repr


class Chest(AbstractEntity):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.requested_at: datetime = datetime.utcnow()

    def __repr__(self) -> str:
        info = {
            "id": self.id,
            "orbs": self.orbs,
            "diamonds": self.diamonds,
            "shard_id": self.shard_id,
            "shard_type": self.shard_type,
            "keys": self.keys,
            "count": self.count,
            "delta": self.delta,
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return f"Chest; count: {self.count}, new in {self.delta}"

    @property
    def orbs(self) -> int:
        return self.options.get("orbs", 0)

    @property
    def diamonds(self) -> int:
        return self.options.get("diamonds", 0)

    @property
    def shard_id(self) -> int:
        return self.options.get("shard_id", 0)

    @property
    def shard_type(self) -> ShardType:
        return ShardType.from_value(self.options.get("shard_type", 0))

    @property
    def keys(self) -> int:
        return self.options.get("keys", 0)

    @property
    def count(self) -> int:
        return self.options.get("count", 0)

    @property
    def seconds(self) -> int:
        return self.options.get("seconds", 0)

    @property
    def delta(self) -> timedelta:
        return timedelta(seconds=self.seconds)

    @property
    def ready_at(self) -> datetime:
        return self.requested_at + self.delta


class Quest(AbstractEntity):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.requested_at: datetime = datetime.utcnow()

    def __repr__(self) -> str:
        info = {
            "id": self.id,
            "name": repr(self.name),
            "type": self.type,
            "amount": self.amount,
            "reward": self.reward,
            "delta": self.delta,
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        if self.type is QuestType.UNKNOWN:
            return f"Quest {self.name!r}; reward: {self.reward}, new in {self.delta}"
        return (
            f"Quest {self.name!r}; collect: {self.amount} "
            f"{self.type.name.lower()}, reward: {self.reward}, new in {self.delta}"
        )

    @property
    def type(self) -> QuestType:
        return QuestType.from_value(self.options.get("type", 0))

    @property
    def amount(self) -> int:
        return self.options.get("amount", 0)

    @property
    def reward(self) -> int:
        return self.options.get("reward", 0)

    @property
    def name(self) -> str:
        return self.options.get("name", "")

    @property
    def seconds(self) -> int:
        return self.options.get("seconds", 0)

    @property
    def delta(self) -> timedelta:
        return timedelta(seconds=self.seconds)

    @property
    def new_at(self) -> datetime:
        return self.requested_at + self.delta
