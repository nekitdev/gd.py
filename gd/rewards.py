from datetime import datetime, timedelta

from gd.abstract_entity import AbstractEntity
from gd.enums import QuestType, ShardType
from gd.model import ChestModel, QuestModel  # type: ignore
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Optional

__all__ = ("Chest", "Quest")

if TYPE_CHECKING:
    from gd.client import Client  # noqa


class Chest(AbstractEntity):
    """Class that represents reward chests in Geometry Dash.
    This class is derived from :class:`~gd.AbstractEntity`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)

            Return human-readable representation of the chest,
            like ``Chest; count: 13, new in 00:00:42.000000``.

        .. describe:: repr(x)

            Return representation of the chest, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

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

    @classmethod
    def from_model(  # type: ignore
        cls,
        model: ChestModel,
        *,
        client: Optional["Client"] = None,
        count: int = 0,
        seconds: int = 0,
    ) -> "Chest":
        return cls(
            orbs=model.orbs,
            diamonds=model.diamonds,
            shard_id=model.shard_id,
            keys=model.keys,
            count=count,
            seconds=seconds,
            client=client,
        )

    @property
    def orbs(self) -> int:
        """:class:`int`: Amount of orbs the chest will give."""
        return self.options.get("orbs", 0)

    @property
    def diamonds(self) -> int:
        """:class:`int`: Amount of diamonds the chest will give."""
        return self.options.get("diamonds", 0)

    @property
    def shard_id(self) -> int:
        """:class:`int`: ID of shard the chest will give."""
        return self.options.get("shard_id", 0)

    @property
    def shard_type(self) -> ShardType:
        """:class:`~gd.ShardType`: Type of the shard the chest will give."""
        return ShardType.from_value(self.shard_id)

    @property
    def keys(self) -> int:
        """:class:`int`: Amount of keys the chest will give."""
        return self.options.get("keys", 0)

    @property
    def count(self) -> int:
        """:class:`int`: Amount of chests already opened."""
        return self.options.get("count", 0)

    @property
    def seconds(self) -> int:
        """:class:`int`: Amount of seconds until next chest can be opened."""
        return self.options.get("seconds", 0)

    @property
    def delta(self) -> timedelta:
        """:class:`datetime.timedelta`: Amount of seconds until next chest, wrapped in delta."""
        return timedelta(seconds=self.seconds)

    @property
    def ready_at(self) -> datetime:
        """:class:`datetime.datetime`: Timestamp after which the chest can be opened."""
        return self.requested_at + self.delta


class Quest(AbstractEntity):
    """Class that represents quests, or challenges, in Geometry Dash.
    This class is derived from :class:`~gd.AbstractEntity`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)

            Return human-readable representation of the quest,
            like ``Quest Name; collect: 100 orbs, reward: 10, new in 00:00:13.000000``.

        .. describe:: repr(x)

            Return representation of the quest, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
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

    @classmethod
    def from_model(  # type: ignore
        cls, model: QuestModel, *, client: Optional["Client"] = None, seconds: int = 0,
    ) -> "Quest":
        return cls(
            id=model.id,
            type=model.type,
            amount=model.amount,
            reward=model.reward,
            name=model.name,
            client=client,
        )

    @property
    def type(self) -> QuestType:
        """:class:`~gd.QuestType`: Type of a quest requirement."""
        return QuestType.from_value(self.options.get("type", 0))

    @property
    def amount(self) -> int:
        """:class:`int`: Amount of items to collect."""
        return self.options.get("amount", 0)

    @property
    def reward(self) -> int:
        """:class:`int`: Amount of diamonds in reward."""
        return self.options.get("reward", 0)

    @property
    def name(self) -> str:
        """:class:`str`: Name of the quest."""
        return self.options.get("name", "")

    @property
    def seconds(self) -> int:
        """:class:`int`: Seconds until next quest pack."""
        return self.options.get("seconds", 0)

    @property
    def delta(self) -> timedelta:
        """:class:`datetime.timedelta`: Delta until next quest pack."""
        return timedelta(seconds=self.seconds)

    @property
    def new_at(self) -> datetime:
        """:class:`datetime.datetime` Timestamp after which next quest pack can be fetched."""
        return self.requested_at + self.delta
