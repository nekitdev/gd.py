from __future__ import annotations

from enum import Enum

__all__ = ("DEMON", "Difficulty", "DemonDifficulty")


class Difficulty(Enum):
    """Represents level difficulties."""

    UNKNOWN = 0
    """*Unknown* difficulty."""

    AUTO = 1
    """*Auto* difficulty."""

    EASY = 2
    """*Easy* difficulty."""

    NORMAL = 3
    """*Normal* difficulty."""

    HARD = 4
    """*Hard* difficulty."""

    HARDER = 5
    """*Harder* difficulty."""

    INSANE = 6
    """*Insane* difficulty."""

    UNSPECIFIED_DEMON = 7
    """*Unspecified Demon* difficulty."""

    EASY_DEMON = 8
    """*Easy Demon* difficulty."""

    MEDIUM_DEMON = 9
    """*Medium Demon* difficulty."""

    HARD_DEMON = 10
    """*Hard Demon* difficulty."""

    INSANE_DEMON = 11
    """*Insane Demon* difficulty."""

    EXTREME_DEMON = 12
    """*Extreme Demon* difficulty."""

    NA = UNKNOWN
    """*N/A* difficulty."""

    DEFAULT = UNKNOWN
    """*Default* difficulty."""

    def into_level_difficulty(self) -> LevelDifficulty:
        return DIFFICULTY_TO_LEVEL_DIFFICULTY[self]

    def into_demon_difficulty(self) -> DemonDifficulty:
        """Converts the difficulty into [`DemonDifficulty`][gd.enums.difficulties.DemonDifficulty].

        Raises:
            KeyError: If the difficulty does not correspond to any demon difficulty.

        Returns:
            The converted demon difficulty.
        """
        return DIFFICULTY_TO_DEMON_DIFFICULTY[self]

    def is_unknown(self) -> bool:
        """Checks if the difficulty is [`UNKNOWN`][gd.enums.difficulties.Difficulty.UNKNOWN].

        Returns:
            Whether the difficulty is [`UNKNOWN`][gd.enums.difficulties.Difficulty.UNKNOWN].
        """
        return self is type(self).UNKNOWN

    def is_auto(self) -> bool:
        """Checks if the difficulty is [`AUTO`][gd.enums.difficulties.Difficulty.AUTO].

        Returns:
            Whether the difficulty is [`AUTO`][gd.enums.difficulties.Difficulty.AUTO].
        """
        return self is type(self).AUTO

    def is_unspecified_demon(self) -> bool:
        """Checks if the difficulty is
        [`UNSPECIFIED_DEMON`][gd.enums.difficulties.Difficulty.UNSPECIFIED_DEMON].

        Returns:
            Whether the difficulty is
                [`UNSPECIFIED_DEMON`][gd.enums.difficulties.Difficulty.UNSPECIFIED_DEMON].
        """
        return self is type(self).UNSPECIFIED_DEMON

    def is_specified_demon(self) -> bool:
        """Checks if the difficulty is in [`DEMON`][gd.enums.difficulties.DEMON].

        Returns:
            Whether the difficulty is in [`DEMON`][gd.enums.difficulties.DEMON].
        """
        return self in DEMON

    def is_demon(self) -> bool:
        """Checks if the difficulty is *demon*, specified or otherwise.

        This is equivalent to:

        ```python
        difficulty.is_unspecified_demon() or difficulty.is_specified_demon()
        ```

        Returns:
            Whether the difficulty is *demon*.
        """
        return self.is_unspecified_demon() or self.is_specified_demon()

    def clamp_demon(self) -> Difficulty:
        """Clamps all specified demon difficulties to
        [`UNSPECIFIED_DEMON`][gd.enums.difficulties.Difficulty.UNSPECIFIED_DEMON].

        Returns:
            The demon-clamped difficulty.
        """
        if self.is_specified_demon():
            return type(self).UNSPECIFIED_DEMON

        return self


DEMON = {
    Difficulty.EASY_DEMON,
    Difficulty.MEDIUM_DEMON,
    Difficulty.HARD_DEMON,
    Difficulty.INSANE_DEMON,
    Difficulty.EXTREME_DEMON,
}
"""The set of *demon* difficulties."""


class LevelDifficulty(Enum):
    UNKNOWN = -1
    UNSPECIFIED_DEMON = -2
    AUTO = -3
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    EASY_DEMON = 6
    MEDIUM_DEMON = 7
    HARD_DEMON = 8
    INSANE_DEMON = 9
    EXTREME_DEMON = 10

    NA = UNKNOWN

    DEFAULT = UNKNOWN

    def into_difficulty(self) -> Difficulty:
        return LEVEL_DIFFICULTY_TO_DIFFICULTY[self]


LEVEL_DIFFICULTY_TO_DIFFICULTY = {
    LevelDifficulty.UNKNOWN: Difficulty.UNKNOWN,
    LevelDifficulty.AUTO: Difficulty.AUTO,
    LevelDifficulty.EASY: Difficulty.EASY,
    LevelDifficulty.NORMAL: Difficulty.NORMAL,
    LevelDifficulty.HARD: Difficulty.HARD,
    LevelDifficulty.HARDER: Difficulty.HARDER,
    LevelDifficulty.INSANE: Difficulty.INSANE,
    LevelDifficulty.UNSPECIFIED_DEMON: Difficulty.UNSPECIFIED_DEMON,
    LevelDifficulty.EASY_DEMON: Difficulty.EASY_DEMON,
    LevelDifficulty.MEDIUM_DEMON: Difficulty.MEDIUM_DEMON,
    LevelDifficulty.HARD_DEMON: Difficulty.HARD_DEMON,
    LevelDifficulty.INSANE_DEMON: Difficulty.INSANE_DEMON,
    LevelDifficulty.EXTREME_DEMON: Difficulty.EXTREME_DEMON,
}

DIFFICULTY_TO_LEVEL_DIFFICULTY = {
    difficulty: level_difficulty
    for level_difficulty, difficulty in LEVEL_DIFFICULTY_TO_DIFFICULTY.items()
}


class DemonDifficulty(Enum):
    """Represents demon difficulties."""

    UNSPECIFIED_DEMON = 0
    """*Unspecified* demon difficulty."""

    EASY_DEMON = 1
    """*Easy* demon difficulty."""

    MEDIUM_DEMON = 2
    """*Medium* demon difficulty."""

    HARD_DEMON = 3
    """*Hard* demon difficulty."""

    INSANE_DEMON = 4
    """*Insane* demon difficulty."""

    EXTREME_DEMON = 5
    """*Extreme* demon difficulty."""

    DEFAULT = UNSPECIFIED_DEMON
    """*Default* demon difficulty."""

    def into_difficulty(self) -> Difficulty:
        """Converts the difficulty into [`Difficulty`][gd.enums.difficulties.Difficulty].

        Returns:
            The converted difficulty.
        """
        return DEMON_DIFFICULTY_TO_DIFFICULTY[self]

    def into_level_difficulty(self) -> LevelDifficulty:
        return DEMON_DIFFICULTY_TO_LEVEL_DIFFICULTY[self]


DEMON_DIFFICULTY_TO_DIFFICULTY = {
    DemonDifficulty.UNSPECIFIED_DEMON: Difficulty.UNSPECIFIED_DEMON,
    DemonDifficulty.EASY_DEMON: Difficulty.EASY_DEMON,
    DemonDifficulty.MEDIUM_DEMON: Difficulty.MEDIUM_DEMON,
    DemonDifficulty.HARD_DEMON: Difficulty.HARD_DEMON,
    DemonDifficulty.INSANE_DEMON: Difficulty.INSANE_DEMON,
    DemonDifficulty.EXTREME_DEMON: Difficulty.EXTREME_DEMON,
}

DIFFICULTY_TO_DEMON_DIFFICULTY = {
    difficulty: demon_difficulty
    for demon_difficulty, difficulty in DEMON_DIFFICULTY_TO_DIFFICULTY.items()
}


DEMON_DIFFICULTY_TO_LEVEL_DIFFICULTY = {  # because GD handles things like that (?)
    DemonDifficulty.UNSPECIFIED_DEMON: LevelDifficulty.UNSPECIFIED_DEMON,
    DemonDifficulty.EASY_DEMON: LevelDifficulty.EASY,
    DemonDifficulty.MEDIUM_DEMON: LevelDifficulty.NORMAL,
    DemonDifficulty.HARD_DEMON: LevelDifficulty.HARD,
    DemonDifficulty.INSANE_DEMON: LevelDifficulty.HARDER,
    DemonDifficulty.EXTREME_DEMON: LevelDifficulty.INSANE,
}
