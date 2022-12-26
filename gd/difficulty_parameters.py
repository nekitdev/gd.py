from typing import Type, TypeVar

from attrs import define

from gd.constants import DEFAULT_AUTO, DEFAULT_DEMON, DEFAULT_DENOMINATOR, DEFAULT_NUMERATOR
from gd.enums import DemonDifficulty, Difficulty, LevelDifficulty

__all__ = ("DEFAULT_DEMON_DIFFICULTY_VALUE", "DifficultyParameters")

DEFAULT_DEMON_DIFFICULTY_VALUE = DemonDifficulty.DEFAULT.value

BASE = 10

DP = TypeVar("DP", bound="DifficultyParameters")


@define()
class DifficultyParameters:
    difficulty_numerator: int = DEFAULT_NUMERATOR
    difficulty_denominator: int = DEFAULT_DENOMINATOR

    demon_difficulty_value: int = DEFAULT_DEMON_DIFFICULTY_VALUE

    auto: bool = DEFAULT_AUTO
    demon: bool = DEFAULT_DEMON

    @classmethod
    def from_difficulty(cls: Type[DP], difficulty: Difficulty) -> DP:
        if difficulty.is_unknown():
            return cls()

        base = BASE

        if difficulty.is_auto():
            level_difficulty = LevelDifficulty.INSANE  # why, RobTop?

            return cls(
                difficulty_numerator=level_difficulty.value * base,
                difficulty_denominator=base,
                auto=True,
            )

        if difficulty.is_specified_demon():
            demon_difficulty = difficulty.into_demon_difficulty()

            demon_difficulty_value = DEMON_DIFFICULTY_TO_VALUE.get(
                demon_difficulty, DEFAULT_DEMON_DIFFICULTY_VALUE
            )

            level_difficulty = demon_difficulty.into_level_difficulty()

            return cls(
                difficulty_numerator=level_difficulty.value * base,
                difficulty_denominator=base,
                demon_difficulty_value=demon_difficulty_value,
                demon=True,
            )

        if difficulty.is_unspecified_demon():
            return cls(demon=True)  # not specifying difficulty parts here

        level_difficulty = difficulty.into_level_difficulty()

        return cls(difficulty_numerator=level_difficulty.value * base, difficulty_denominator=base)

    def is_auto(self) -> bool:
        return self.auto

    def is_demon(self) -> bool:
        return self.demon

    @property
    def level_difficulty(self) -> LevelDifficulty:
        difficulty_numerator = self.difficulty_numerator
        difficulty_denominator = self.difficulty_denominator

        if difficulty_denominator:
            difficulty_value = difficulty_numerator // difficulty_denominator

            if difficulty_value:
                return LevelDifficulty(difficulty_value)

        return LevelDifficulty.DEFAULT

    @property
    def demon_difficulty(self) -> DemonDifficulty:
        return VALUE_TO_DEMON_DIFFICULTY.get(
            self.demon_difficulty_value, DemonDifficulty.HARD_DEMON
        )

    def into_difficulty(self) -> Difficulty:
        if self.is_auto():
            return Difficulty.AUTO

        if self.is_demon():
            return self.demon_difficulty.into_difficulty()

        return self.level_difficulty.into_difficulty()


VALUE_TO_DEMON_DIFFICULTY = {
    3: DemonDifficulty.EASY_DEMON,
    4: DemonDifficulty.MEDIUM_DEMON,
    5: DemonDifficulty.INSANE_DEMON,
    6: DemonDifficulty.EXTREME_DEMON,
}

DEMON_DIFFICULTY_TO_VALUE = {
    demon_difficulty: value for value, demon_difficulty in VALUE_TO_DEMON_DIFFICULTY.items()
}
