from enum import Enum, Flag

__all__ = ("RateType", "RateFilter")


class SpecialRateType(Enum):
    NONE = 0
    EPIC = 1
    LEGENDARY = 2
    MYTHIC = 3

    DEFAULT = NONE

    def is_none(self) -> bool:
        return self is type(self).NONE

    def is_epic(self) -> bool:
        return self is type(self).EPIC

    def is_legendary(self) -> bool:
        return self is type(self).LEGENDARY

    def is_mythic(self) -> bool:
        return self is type(self).MYTHIC

    def is_default(self) -> bool:
        return self is type(self).DEFAULT


class RateType(Flag):
    """Represents rate types."""

    NONE = 0
    """None."""

    NOT_RATED_ONLY = 1 << 0
    """Non-rated-only levels."""

    RATED_ONLY = 1 << 1
    """Rated-only levels."""

    FEATURED_ONLY = 1 << 2
    """Featured-only levels."""

    EPIC_ONLY = 1 << 3
    """Epic-only levels."""

    LEGENDARY_ONLY = 1 << 4
    """Legendary-only levels."""

    MYTHIC_ONLY = 1 << 5
    """Mythic-only levels."""

    NOT_RATED = NOT_RATED_ONLY | NONE
    """Non-rated levels."""

    RATED = NOT_RATED | RATED_ONLY
    """Rated or non-rated levels."""

    FEATURED = RATED | FEATURED_ONLY
    """Featured, rated or non-rated levels."""

    EPIC = FEATURED | EPIC_ONLY
    """Epic, featured, rated or non-rated levels."""

    LEGENDARY = EPIC | LEGENDARY_ONLY
    """Legendary, epic, featured, rated or non-rated levels."""

    MYTHIC = LEGENDARY | MYTHIC_ONLY
    """Mythic, legendary, epic, featured, rated or non-rated levels."""

    DEFAULT = NONE
    """The default rate type."""

    def is_none(self) -> bool:
        """Checks if the rate type is [`NONE`][gd.enums.rates.RateType.NONE].

        Returns:
            Whether the rate type is [`NONE`][gd.enums.rates.RateType.NONE].
        """
        return self is type(self).NONE

    def is_not_rated(self) -> bool:
        """Checks if the rate type contains [`NOT_RATED`][gd.enums.rates.RateType.NOT_RATED].

        Returns:
            Whether the rate type contains [`NOT_RATED`][gd.enums.rates.RateType.NOT_RATED].
        """
        return type(self).NOT_RATED_ONLY in self

    def is_rated(self) -> bool:
        """Checks if the rate type contains [`RATED`][gd.enums.rates.RateType.RATED].

        Returns:
            Whether the rate type contains [`RATED`][gd.enums.rates.RateType.RATED].
        """
        return type(self).RATED_ONLY in self

    def is_featured(self) -> bool:
        """Checks if the rate type contains [`FEATURED`][gd.enums.rates.RateType.FEATURED].

        Returns:
            Whether the rate type contains [`FEATURED`][gd.enums.rates.RateType.FEATURED].
        """
        return type(self).FEATURED_ONLY in self

    def is_epic(self) -> bool:
        """Checks if the rate type contains [`EPIC`][gd.enums.rates.RateType.EPIC].

        Returns:
            Whether the rate type contains [`EPIC`][gd.enums.rates.RateType.EPIC].
        """
        return type(self).EPIC_ONLY in self

    def is_legendary(self) -> bool:
        """Checks if the rate type contains [`LEGENDARY`][gd.enums.rates.RateType.LEGENDARY].

        Returns:
            Whether the rate type contains [`LEGENDARY`][gd.enums.rates.RateType.LEGENDARY].
        """
        return type(self).LEGENDARY_ONLY in self

    def is_mythic(self) -> bool:
        """Checks if the rate type contains [`MYTHIC`][gd.enums.rates.RateType.MYTHIC].

        Returns:
            Whether the rate type contains [`MYTHIC`][gd.enums.rates.RateType.MYTHIC].
        """
        return type(self).MYTHIC_ONLY in self

    def is_default(self) -> bool:
        """Checks if the rate type is [`DEFAULT`][gd.enums.rates.RateType.DEFAULT].

        Returns:
            Whether the rate type is [`DEFAULT`][gd.enums.rates.RateType.DEFAULT].
        """
        return self is type(self).DEFAULT


class RateFilter(Enum):
    """Represents rate filters."""

    NOT_RATED = 0
    """Non-rated levels."""

    RATED = 1
    """Rated levels."""

    FEATURED = 2
    """Featured levels."""

    EPIC = 3
    """Epic levels."""

    LEGENDARY = 4
    """Legendary levels."""

    MYTHIC = 5
    """Mythic levels."""
