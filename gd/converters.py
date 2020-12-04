from gd.crypto import Key, decode_robtop_str, encode_robtop_str
from gd.enums import DemonDifficulty, LevelDifficulty
from gd.text_utils import make_repr
from gd.typing import Any, Dict, Optional, Tuple, Union

__all__ = (
    "GameVersion",
    "Password",
    "Version",
    "get_actual_difficulty",
)


class Version:
    """Class that represents version of anything.

    .. container:: operations

        .. describe:: x == y

            Check if two versions are equal.

        .. describe:: x != y

            Check if two versions are not equal.

        .. describe:: x > y

            Check if one version is strictly greater than another.

        .. describe:: x >= y

            Check if one version is greater than or equal to another.

        .. describe:: x < y

            Check if one version is strictly lower than another.

        .. describe:: x <= y

            Check if one version is lower than or equal to another.

        .. describe:: str(x)

            Return short representation of the version; for ``Version(x, y)``, return ``x.y``.

        .. describe:: repr(x)

            Return representation of the version, useful for debugging.

    Parameters
    ----------
    major: :class:`int`
        Major part of the version.

    minor: :class:`int`
        Minor part of the version.
    """

    def __init__(self, major: int, minor: int) -> None:
        self._major = major
        self._minor = minor

    def __json__(self) -> str:
        return str(self)

    @property
    def major(self) -> int:
        """:class:`int`: Major part of the version."""
        return self._major

    @property
    def minor(self) -> int:
        """:class:`int`: Minor part of the version."""
        return self._minor

    @property
    def parts(self) -> Tuple[int, int]:
        """Tuple[:class:`int`, :class:`int`]: All parts of the version, as tuple object."""
        return (self._major, self._minor)

    def __repr__(self) -> str:
        info = {"major": self.major, "minor": self.minor}
        return make_repr(self, info)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (self.major, self.minor) == (other.major, other.minor)

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (self.major, self.minor) != (other.major, other.minor)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (self.major, self.minor) < (other.major, other.minor)

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (self.major, self.minor) > (other.major, other.minor)

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __ge__(self, other: Any) -> bool:
        return self > other or self == other

    @classmethod
    def from_number(cls, number: int) -> "Version":
        """Create a version from number, e.g. ``21`` -> ``2.1``."""
        major, minor = divmod(number, 10)
        return cls(major, minor)

    def to_number(self) -> int:
        """Convert the version to a number, e.g. ``1.9`` -> ``19``."""
        return self.major * 10 + self.minor


class GameVersion(Version):
    """Derived from :class:`~gd.Version`, contains additional features to convert game version."""

    @classmethod
    def from_robtop_number(cls, number: int) -> "GameVersion":
        """Convert RobTop's ``number`` to :class:`~gd.GameVersion`."""
        if 0 < number < 8:
            return cls(1, number - 1)

        elif number == 10:
            return cls(1, 7)

        elif number < 10:
            raise ValueError(f"Invalid version provided: {number}.")

        major, minor = divmod(number, 10)

        return cls(major, minor)

    def to_robtop_number(self) -> int:
        """Convert :class:`~gd.GameVersion` to a RobTop's number."""
        major = self._major
        minor = self._minor

        if major == 1:
            if minor == 7:
                return 10

            elif minor < 7:
                return minor + 1

        return major * 10 + minor

    @classmethod
    def from_robtop(cls, string: str) -> "GameVersion":
        """Same as :meth:`~gd.GameVersion.from_robtop_number`, but operates on ``string``."""
        return cls.from_robtop_number(int(string))

    def to_robtop(self) -> str:
        """Same as :meth:`~gd.GameVersion.to_robtop_number`, but returns a string."""
        return str(self.to_robtop_number())


class Password:
    """Class that represents passwords.

    .. container:: operations

        .. describe:: str(x)

            Return a human-friendly description of the password.
            For example, ``copyable, password 101010``.

        .. describe:: repr(x)

            Return representation of the password, useful for debugging.

    Parameters
    ----------
    password: Optional[Union[:class:`int`, :class:`str`]]
        Actual password, as a number or a string.

    copyable: :class:`bool`
        Whether passwords implies that something is copyable.
        If ``True`` and ``password`` is ``None``, free copy is assumed.
    """

    _ADD = 1_000_000

    def __init__(self, password: Optional[Union[int, str]] = None, copyable: bool = True) -> None:
        if password is None:
            self._password = None

        else:
            self._password = int(password)

            if self._password >= self._ADD:
                raise ValueError(f"Password is too large: {password}.")

        self._copyable = bool(copyable)

    def __json__(self) -> Dict[str, Union[Optional[int], bool]]:
        return {"password": self.password, "copyable": self.copyable}

    def __str__(self) -> str:
        if self.copyable:
            if self.password is None:
                return "copyable, no password"
            else:
                return f"copyable, password {self.password}"
        return "not copyable"

    def __repr__(self) -> str:
        info = {"password": self.password, "copyable": self.copyable}
        return make_repr(self, info)

    @property
    def copyable(self) -> bool:
        """:class:`bool`: Whether password implies that something is copyable."""
        return self._copyable

    @property
    def password(self) -> Optional[int]:
        """Optional[:class:`int`]: Actual password, ``None`` if not given."""
        return self._password

    @classmethod
    def from_robtop_number(cls, number: int) -> "Password":
        """Create :class:`~gd.Password` from ``number``."""
        if number == 0:
            return cls(None, False)

        if number == 1:
            return cls(None, True)

        return cls(number % cls._ADD, True)

    def to_robtop_number(self) -> int:
        """Convert :class:`~gd.Password` to a number."""
        if self._copyable:
            if self._password is None:
                return 1

            else:
                return self._password + self._ADD

        else:
            return 0

    @classmethod
    def from_robtop(cls, string: str) -> "Password":
        """Same as :meth:`~gd.Password.from_robtop_number`, except it attempts decoding."""
        try:
            password = decode_robtop_str(string, Key.LEVEL_PASSWORD)  # type: ignore

        except Exception:  # noqa
            password = string

        if password.isdigit():
            return cls.from_robtop_number(int(password))

        else:
            return cls(None, False)

    def to_robtop(self, encode: bool = True) -> str:
        """Same as :meth:`~gd.Password.to_robtop_number`, except it optionally applies encoding."""
        number = self.to_robtop_number()

        if not number or not encode:
            return str(number)

        else:
            return encode_robtop_str(str(number), Key.LEVEL_PASSWORD)  # type: ignore


VALUE_TO_LEVEL_DIFFICULTY = {
    0: LevelDifficulty.NA,
    1: LevelDifficulty.EASY,
    2: LevelDifficulty.NORMAL,
    3: LevelDifficulty.HARD,
    4: LevelDifficulty.HARDER,
    5: LevelDifficulty.INSANE,
    6: LevelDifficulty.DEMON,
}

VALUE_TO_DEMON_DIFFICULTY = {
    0: DemonDifficulty.HARD_DEMON,
    3: DemonDifficulty.EASY_DEMON,
    4: DemonDifficulty.MEDIUM_DEMON,
    5: DemonDifficulty.INSANE_DEMON,
    6: DemonDifficulty.EXTREME_DEMON,
}


def value_to_level_difficulty(value: int) -> LevelDifficulty:
    return VALUE_TO_LEVEL_DIFFICULTY.get(value, LevelDifficulty.NA)  # type: ignore


def value_to_demon_difficulty(value: int) -> DemonDifficulty:
    return VALUE_TO_DEMON_DIFFICULTY.get(value, DemonDifficulty.HARD_DEMON)  # type: ignore


def get_actual_difficulty(
    level_difficulty: int, demon_difficulty: int, is_auto: bool, is_demon: bool
) -> Union[LevelDifficulty, DemonDifficulty]:
    """Get real level difficulty from given parameters.

    Parameters
    ----------
    level_difficulty: :class:`int`
        Number that represents level difficulty.

    demon_difficulty: :class:`int`
        Number that represents level demon difficulty.

    is_auto: :class:`bool`
        Whether the level is auto.

    is_demon: :class:`bool`
        Whether the level is demon.

    Returns
    -------
    Union[:class:`~gd.LevelDifficulty`, :class:`~gd.DemonDifficulty`]
        Level or demon difficulty, based on parameters.
    """
    if is_auto:
        return LevelDifficulty.AUTO  # type: ignore

    elif is_demon:
        return value_to_demon_difficulty(demon_difficulty)

    return value_to_level_difficulty(level_difficulty)
