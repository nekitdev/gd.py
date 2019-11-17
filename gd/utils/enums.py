import functools
from enum import Enum

from typing import Union

from ..errors import FailedConversion

__all__ = (
    'NEnum',
    'IconType',
    'MessagePolicyType',
    'CommentPolicyType',
    'FriendRequestPolicyType',
    'StatusLevel',
    'LevelLength',
    'LevelDifficulty',
    'DemonDifficulty',
    'TimelyType',
    'CommentType',
    'MessageOrRequestType',
    'CommentStrategy',
    'LeaderboardStrategy',
    'LevelLeaderboardStrategy',
    'SearchStrategy',
    'GauntletEnum'
)

def _name_to_enum(x: str):
    return x.upper().replace(' ', '_')


def _enum_to_name(x: Enum):
    name = x.name
    return name if name == 'XL' else name.replace('_', ' ').title()


def value_to_enum(enum: Enum, x: Union[int, str, Enum]):
    """Tries to convert given value to Enum object.

    Example:

    .. code-block:: python3

        from gd.utils import value_to_enum

        enum = gd.IconType

        value_to_enum(enum, 0)                -> gd.IconType.CUBE
        value_to_enum(enum, 'cube')           -> gd.IconType.CUBE
        value_to_enum(enum, gd.IconType.CUBE) -> gd.IconType.CUBE

    Parameters
    ----------
    enum: :class:`enum.Enum`
        Instance of *Enum* to convert ``x`` to.

    x: Union[:class:`int`, :class:`str`, :class:`enum.Enum`]
        Object to convert to ``enum``.

    Returns
    -------
    :class:`enum.Enum`
        Result of converting ``x`` to ``enum``.

    Raises
    ------
    :exc:`.FailedConversion`
        Failed to convert ``x`` to ``enum``.
    """
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

        # let's raise it here, so if it is raised, we can tell that invalid type was given.
        raise ValueError

    except ValueError:
        raise FailedConversion(enum=enum, value=x) from None


@functools.total_ordering
class NEnum(Enum):
    """Subclass of :class:`enum.Enum`, used for creating enums in gd.py.

    .. container:: operations

        .. describe:: x == y

            Checks if two enums are equal.

        .. describe:: x != y

            Checks if two enums are not equal.

        .. describe:: x > y

            Checks if value of x is higher than value of y.
            Raises an error if values are not instances of :class:`int`.

        .. describe:: x < y

            Checks if value of x is lower than value of y.
            Raises an error on not-integer type as well.

        .. describe:: x >= y

            Same as *x == y or x > y*.

        .. describe:: x <= y

            Same as *x == y or x < y*.

        .. describe:: hash(x)

            Return the enum's hash.

        .. describe:: str(x)

            Returns :attr:`.NEnum.desc`.
    """

    def __str__(self):
        return self.desc

    def __repr__(self):
        return '<gd.{0}.{1}: {2} ({3})>'.format(
            self.__class__.__name__, self.name, self.value, self.desc
        )

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.value == other.value

    def __ne__(self, other):
        return isinstance(other, type(self)) and self.value != other.value

    def __gt__(self, other):
        return isinstance(other, type(self)) and self.value > other.value

    def __hash__(self):
        return hash(self.__repr__())

    @property
    def desc(self):
        """:class:`str`: More readable version of the name, e.g.

        .. code-block:: python3

            gd.SearchStrategy.BY_USER.desc -> 'By User'.
        """
        return _enum_to_name(self)

    @classmethod
    def as_dict(cls):
        return {enum.value: enum.name.lower() for enum in iter(cls)}

    @classmethod
    def from_value(cls, value: Union[int, str]):
        """Returns *Enum* with given value.

        .. note::

            This can only be called in a class **derived** from :class:`.NEnum`,
            so *NEnum.from_value(...)* will raise an error.

            Example:

            .. code-block:: python3

                mod = gd.StatusLevel.from_value('moderator')

                hall_of_fame = gd.SearchStrategy.from_value('hall of fame')

        Parameters
        ----------
        value: Union[:class:`int`, :class:`str`]
            A value to make *Enum* from.

        Returns
        -------
        :class:`.NEnum`
            Enum from the :class:`.NEnum` subclass.

        Raises
        ------
        :exc:`.FailedConversion`
            Failed to convert ``value`` to *Enum*.

        :exc:`TypeError`
            Invalid *Enum* class was given.
        """
        assert cls is not NEnum
        return value_to_enum(cls, value)

class IconType(NEnum):
    """An enumeration of icon types."""
    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6


class MessagePolicyType(NEnum):
    """An enumeration for message policy."""
    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class CommentPolicyType(NEnum):
    """An enumeration for comment policy."""
    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class FriendRequestPolicyType(NEnum):
    """An enumeration for friend request policy."""
    OPENED = 0
    CLOSED = 1


class StatusLevel(NEnum):
    """An enumeration for Geometry Dash Status."""
    USER = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2


class LevelLength(NEnum):
    """An enumeration for level lengths."""
    NA = -1
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4


class LevelDifficulty(NEnum):
    """An enumeration for level difficulties."""
    NA = -1
    AUTO = -3
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    DEMON = -2


class DemonDifficulty(NEnum):
    """An enumeration for demon difficulties."""
    EASY_DEMON = 1
    MEDIUM_DEMON = 2
    HARD_DEMON = 3
    INSANE_DEMON = 4
    EXTREME_DEMON = 5


class TimelyType(NEnum):
    """An enumeration for timely types."""
    NOT_TIMELY = 0
    DAILY = 1
    WEEKLY = 2


class CommentType(NEnum):
    """An enumeration for comment objects."""
    LEVEL = 0
    PROFILE = 1


class MessageOrRequestType(NEnum):
    """An enumeration for message and friend request objects."""
    NORMAL = 0
    SENT = 1


class CommentStrategy(NEnum):
    """An enumeration for comment searching."""
    RECENT = 0
    MOST_LIKED = 1


class LeaderboardStrategy(NEnum):
    """An enumeration for getting leaderboard users."""
    PLAYERS = 0
    FRIENDS = 1
    RELATIVE = 2
    CREATORS = 3


class LevelLeaderboardStrategy(NEnum):
    """An enumeration for getting level leaderboard."""
    FRIENDS = 0
    ALL = 1
    WEEKLY = 2


class GauntletEnum(NEnum):
    """An enumeration for gauntlets."""
    FIRE = 1
    ICE = 2
    POISON = 3
    SHADOW = 4
    LAVA = 5
    BONUS = 6
    CHAOS = 7
    DEMON = 8
    TIME = 9
    CRYSTAL = 10
    MAGIC = 11
    SPIKE = 12
    MONSTER = 13
    DOOM = 14
    DEATH = 15


class SearchStrategy(NEnum):
    """An enumeration for search strategy."""
    REGULAR = 0
    MOST_DOWNLOADED = 1
    MOST_LIKED = 2
    TRENDING = 3
    RECENT = 4
    BY_USER = 5
    FEATURED = 6
    MAGIC = 7
    SEARCH_MANY = 10
    AWARDED = 11
    FOLLOWED = 12
    FRIENDS = 13
    HALL_OF_FAME = 16
    WORLD = 17
