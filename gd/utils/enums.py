import functools
from enum import Enum

from typing import Union

from ..errors import FailedConversion

__all__ = (
    'IconType',
    'MessagePolicyType',
    'CommentPolicyType',
    'FriendRequestPolicyType',
    'StatusLevel',
    'LevelLength',
    'LevelDifficulty',
    'DemonDifficulty',
    'TimelyType',
    'DifficultyFilter',
    'DemonFilter',
    'SearchStrategy'
)

def _name_to_enum(x: str):
    return x.upper().replace(' ', '_')

def _are_same_enums(e1, e2):
    return type(e1) == type(e2)

def _are_both_enums(e1, e2):
    return all(isinstance(e, Enum) for e in (e1, e2))

def _ensure_comp(e1, e2):
    ok = True
    if _are_both_enums(e1, e2):
        ok = _are_same_enums(e1, e2)
    return ok

@functools.total_ordering
class NEnum(Enum):
    def __int__(self):
        return (self._value_ if isinstance(self._value_, int) else -1)

    def __str__(self):
        return self.desc

    def __repr__(self):
        return '<gd.{0}.{1}: {2} ({3})>'.format(
            self.__class__.__name__, self._name_, self._value_, self.desc
        )

    @property
    def desc(self):
        # return somewhat formatted name
        name = self._name_
        return (name if name == 'XL' else name.replace('_', ' ').title())
    
    def __eq__(self, other):
        return int(self) == int(other) and _ensure_comp(self, other)

    def __ne__(self, other):
        return int(self) != int(other) and _ensure_comp(self, other)

    def __gt__(self, other):
        return int(self) > int(other) and _ensure_comp(self, other)


def _value_to_enum(enum, x: Union[int, str, Enum]):
    """Tries to convert given value to Enum object."""
    try:
        # if int -> enum of value x
        if isinstance(x, int):
            return enum(x)

        # if str -> enum of name x (converted)
        elif isinstance(x, str):
            return enum[_name_to_enum(x)]

        # if enum -> enum of value x.value
        elif isinstance(x, NEnum):
            return enum(x.value)

    except ValueError:
        raise FailedConversion(enum=enum, value=x) from None


class IconType(NEnum):
    """An enumeration of icon types.

    .. code-block:: python3

        CUBE = 0
        SHIP = 1
        BALL = 2
        UFO = 3
        WAVE = 4
        ROBOT = 5
        SPIDER = 6
    """
    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6


class MessagePolicyType(NEnum):
    """An enumeration for message policy.

    .. code-block:: python3

        OPENED_TO_ALL = 0
        OPENED_TO_FRIENDS_ONLY = 1
        CLOSED = 2
    """
    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class CommentPolicyType(NEnum):
    """An enumeration for comment policy.

    .. code-block:: python3

        OPENED_TO_ALL = 0
        OPENED_TO_FRIENDS_ONLY = 1
        CLOSED = 2
    """
    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class FriendRequestPolicyType(NEnum):
    """An enumeration for friend request policy.

    .. code-block:: python3

        OPENED = 0
        CLOSED = 1
    """
    OPENED = 0
    CLOSED = 1


class StatusLevel(NEnum):
    """An enumeration for Geometry Dash Status.

    .. code-block:: python3

        USER = 0
        MODERATOR = 1
        ELDER_MODERATOR = 2
    """
    USER = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2


class LevelLength(NEnum):
    """An enumeration for level lengths.

    .. code-block:: python3

        TINY = 0
        SHORT = 1
        MEDIUM = 2
        LONG = 3
        XL = 4
    """
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4


class LevelDifficulty(NEnum):
    """An enumeration for level difficulties.

    .. code-block:: python3

        NA = -1
        AUTO = -2
        EASY = 1
        NORMAL = 2
        HARD = 3
        HARDER = 4
        INSANE = 5
        DEMON = -3
    """
    NA = -1
    AUTO = -2
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    DEMON = -3


class DemonDifficulty(NEnum):
    """An enumeration for demon difficulties.

    .. code-block:: python3

        EASY_DEMON = 1
        MEDIUM_DEMON = 2
        HARD_DEMON = 3
        INSANE_DEMON = 4
        EXTREME_DEMON = 5
    """
    EASY_DEMON = 1
    MEDIUM_DEMON = 2
    HARD_DEMON = 3
    INSANE_DEMON = 4
    EXTREME_DEMON = 5

class TimelyType(NEnum):
    """An enumeration for timely types.

    .. code-block:: python3

        NOT_TIMELY = 0
        DAILY = 1
        WEEKLY = 2
    """
    NOT_TIMELY = 0
    DAILY = 1
    WEEKLY = 2

class DifficultyFilter(NEnum):
    """An enumeration for difficulty filters.

    .. code-block:: python3

        EASY = 1
        NORMAL = 2
        HARD = 3
        HARDER = 4
        INSANE = 5
        DEMON = -1
        NA = -1
    """
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    DEMON = -1
    NA = -1  # NA is overriden, but it does not matter in our case.

class DemonFilter(NEnum):
    """An enumeration for demon difficulty filters.

    .. code-block:: python3

        EASY = 1
        MEDIUM = 2
        HARD = 3
        INSANE = 4
        EXTREME = 5
    """
    EASY = 1
    MEDIUM = 2
    HARD = 3
    INSANE = 4
    EXTREME = 5


class SearchStrategy(NEnum):
    """An enumeration for search strategy.

    .. code-block:: python3

        REGULAR = 0
        MOST_DOWNLOADED = 1
        MOST_LIKED = 2
        TRENDING = 3
        RECENT = 4
        BY_USER = 5
        FEATURED = 6
        MAGIC = 7
        AWARDED = 11
        FOLLOWED = 12
        HALL_OF_FAME = 16
    """
    REGULAR = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    BY_USER = 5
    FEATURED = 6
    MAGIC = 7
    AWARDED = 11
    FOLLOWED = 12
    HALL_OF_FAME = 16