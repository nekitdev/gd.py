import functools
import enum

from gd.utils.text_tools import get_module

from gd.typing import Any, Dict, Union
from gd.errors import FailedConversion

__all__ = (
    "Enum",
    "IconType",
    "MessagePolicyType",
    "CommentPolicyType",
    "FriendRequestPolicyType",
    "StatusLevel",
    "LevelLength",
    "LevelDifficulty",
    "DemonDifficulty",
    "TimelyType",
    "CommentType",
    "MessageOrRequestType",
    "CommentStrategy",
    "LeaderboardStrategy",
    "LevelLeaderboardStrategy",
    "SearchStrategy",
    "GauntletEnum",
    "ServerError",
)


def _name_to_enum(x: str) -> str:
    return x.upper().replace(" ", "_")


def _is_upper(string: str) -> bool:
    return string.upper() == string


def _enum_to_name(x: enum.Enum) -> str:
    name = x.name.strip("_")
    return name if (name in ("NA", "XL") or not _is_upper(name)) else name.replace("_", " ").title()


def value_to_enum(enum: enum.Enum, x: Union[int, str, enum.Enum]) -> enum.Enum:
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
        if isinstance(x, (float, int)):
            return enum(x)

        # if str -> enum of name x (converted)
        elif isinstance(x, str):
            try:
                return enum[_name_to_enum(x)]
            except KeyError:
                try:
                    return enum[x]
                except KeyError:
                    return enum(x)

        # if enum -> enum of value x.value
        elif isinstance(x, Enum):
            return enum(x.value)

        # let's raise it here, so if it is raised, we can tell that invalid type was given.
        raise ValueError

    except (KeyError, ValueError):
        raise FailedConversion(enum=enum, value=x) from None


@functools.total_ordering
class Enum(enum.Enum):
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

            Returns :attr:`.Enum.desc`.
    """

    def __str__(self) -> str:
        return self.desc

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        module = get_module(self.__module__)

        return f"<{module}.{cls_name}.{self.name}: {self.value} ({self.desc})>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value == other.value

    def __ne__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value != other.value

    def __gt__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.value > other.value

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def _json(self) -> Any:
        return self.value

    @property
    def desc(self) -> str:
        """:class:`str`: More readable version of the name, e.g.

        .. code-block:: python3

            gd.SearchStrategy.BY_USER.desc -> 'By User'.
        """
        return _enum_to_name(self)

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        return {name.lower(): enum.value for name, enum in cls.__members__.items()}

    @classmethod
    def from_value(cls, value: Union[int, str]) -> enum.Enum:
        """Returns *Enum* with given value.

        .. note::

            This can only be called in a class **derived** from :class:`.Enum`,
            so *Enum.from_value(...)* will raise an error.

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
        :class:`.Enum`
            Enum from the :class:`.Enum` subclass.

        Raises
        ------
        :exc:`.FailedConversion`
            Failed to convert ``value`` to *Enum*.

        :exc:`TypeError`
            Invalid *Enum* class was given.
        """
        assert cls is not Enum
        return value_to_enum(cls, value)


class IconType(Enum):
    """An enumeration of icon types."""

    CUBE = 0
    SHIP = 1
    BALL = 2
    UFO = 3
    WAVE = 4
    ROBOT = 5
    SPIDER = 6


class MessagePolicyType(Enum):
    """An enumeration for message policy."""

    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class CommentPolicyType(Enum):
    """An enumeration for comment policy."""

    OPENED_TO_ALL = 0
    OPENED_TO_FRIENDS_ONLY = 1
    CLOSED = 2


class FriendRequestPolicyType(Enum):
    """An enumeration for friend request policy."""

    OPENED = 0
    CLOSED = 1


class StatusLevel(Enum):
    """An enumeration for Geometry Dash Status."""

    USER = 0
    MODERATOR = 1
    ELDER_MODERATOR = 2


class LevelLength(Enum):
    """An enumeration for level lengths."""

    NA = -1
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4


class LevelDifficulty(Enum):
    """An enumeration for level difficulties."""

    NA = -1
    AUTO = -3
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    DEMON = -2


class DemonDifficulty(Enum):
    """An enumeration for demon difficulties."""

    NA = -1
    EASY_DEMON = 1
    MEDIUM_DEMON = 2
    HARD_DEMON = 3
    INSANE_DEMON = 4
    EXTREME_DEMON = 5


class TimelyType(Enum):
    """An enumeration for timely types."""

    NOT_TIMELY = 0
    DAILY = 1
    WEEKLY = 2


class CommentType(Enum):
    """An enumeration for comment objects."""

    LEVEL = 0
    PROFILE = 1


class MessageOrRequestType(Enum):
    """An enumeration for message and friend request objects."""

    NORMAL = 0
    SENT = 1


class CommentStrategy(Enum):
    """An enumeration for comment searching."""

    RECENT = 0
    MOST_LIKED = 1


class LeaderboardStrategy(Enum):
    """An enumeration for getting leaderboard users."""

    PLAYERS = 0
    FRIENDS = 1
    RELATIVE = 2
    CREATORS = 3


class LevelLeaderboardStrategy(Enum):
    """An enumeration for getting level leaderboard."""

    FRIENDS = 0
    ALL = 1
    WEEKLY = 2


class GauntletEnum(Enum):
    """An enumeration for gauntlets."""

    UNKNOWN = 0
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


class SearchStrategy(Enum):
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


class ServerError(Enum):
    """An enumeration for server errors."""

    EMAILS_NOT_MATCHING = -99
    LINKED_TO_DIFFERENT_STEAM_ACCOUNT = -12
    ACCOUNT_DISABLED = -11
    LINKED_TO_DIFFERENT_ACCOUNT = -10
    SHORT_USERNAME = -9
    SHORT_PASSWORD = -8
    PASSWORDS_NOT_MATCHING = -7
    INVALID_EMAIL = -6
    INVALID_PASSWORD = -5
    INVALID_USERNAME = -4
    EMAIL_USED = -3
    USERNAME_USED = -2
    GENERIC = -1
