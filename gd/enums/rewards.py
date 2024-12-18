from enum import Enum

__all__ = ("ChestType", "QuestType")


class RewardAction(Enum):
    FETCH = 0
    CLAIM_SMALL = 1
    CLAIM_LARGE = 2

    DEFAULT = FETCH


class ChestType(Enum):
    """Represents chest types."""

    UNKNOWN = 0
    """Unknown chest."""

    SMALL = 1
    """Small chest."""

    LARGE = 2
    """Large chest."""

    DEFAULT = UNKNOWN
    """The default chest type."""


class QuestType(Enum):
    """Represents quest types."""

    UNKNOWN = 0
    """Unknown quest."""

    ORBS = 1
    """Orbs quest."""

    COINS = 2
    """Coins quest."""

    STARS_MOONS = 3
    """Stars/moons quest."""

    DEFAULT = UNKNOWN
    """The default quest type."""


# TODO: shard types, reward items' types
