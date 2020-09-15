from gd.crypto import Key, decode_robtop_str, encode_robtop_str
from gd.enums import DemonDifficulty, LevelDifficulty
from gd.typing import Optional, Union

from gd.text_utils import make_repr

__all__ = (
    "GameVersion",
    "Password",
    "Version",
    "get_difficulty",
)


class Version:
    def __init__(self, major: int, minor: int) -> None:
        self._major = major
        self._minor = minor

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    def __repr__(self) -> str:
        info = {"major": self.major, "minor": self.minor}
        return make_repr(self, info)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    @classmethod
    def from_number(cls, number: int) -> "Version":
        major, minor = divmod(number, 10)
        return cls(major, minor)

    def to_number(self) -> int:
        return self.major * 10 + self.minor


class GameVersion(Version):
    @classmethod
    def from_robtop_number(cls, number: int) -> "GameVersion":
        if 0 < number < 8:
            return cls(1, number - 1)

        elif number == 10:
            return cls(1, 7)

        elif number < 10:
            raise ValueError(f"Invalid version provided: {number}.")

        major, minor = divmod(number, 10)

        return cls(major, minor)

    def to_robtop_number(self) -> int:
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
        return cls.from_robtop_number(int(string))

    def to_robtop(self) -> str:
        return str(self.to_robtop_number())


class Password:
    _ADD = 1_000_000

    def __init__(self, password: Optional[Union[int, str]] = None, copyable: bool = True) -> None:
        if password is None:
            self._password = None

        else:
            self._password = int(password)

            if self._password >= self._ADD:
                raise ValueError(f"Password is too large: {password}.")

        self._copyable = bool(copyable)

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
        return self._copyable

    @property
    def password(self) -> Optional[int]:
        return self._password

    @classmethod
    def from_robtop_number(cls, number: int) -> "Password":
        if number == 0:
            return cls(None, False)

        if number == 1:
            return cls(None, True)

        return cls(number % cls._ADD, True)

    def to_robtop_number(self) -> int:
        if self._copyable:
            if self._password is None:
                return 1

            else:
                return self._password + self._ADD

        else:
            return 0

    @classmethod
    def from_robtop(cls, string: str) -> "Password":
        try:
            password = decode_robtop_str(string, Key.LEVEL_PASSWORD)  # type: ignore

        except Exception:  # noqa
            password = string

        if password.isdigit():
            return cls.from_robtop_number(int(password))

        else:
            return cls(None, False)

    def to_robtop(self) -> str:
        number = self.to_robtop_number()

        if not number:
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


def get_difficulty(
    level_difficulty: int, demon_difficulty: int, is_auto: bool, is_demon: bool
) -> Union[LevelDifficulty, DemonDifficulty]:
    if is_auto:
        return LevelDifficulty.AUTO  # type: ignore

    elif is_demon:
        return value_to_demon_difficulty(demon_difficulty)

    return value_to_level_difficulty(level_difficulty)
