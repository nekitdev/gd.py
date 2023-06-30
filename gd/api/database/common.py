from gd.enums import CollectedCoins

__all__ = (
    # since `1` is used quite some times in the database
    "ONE",
    # affixes, combined in observed ways
    "OFFICIAL",
    "NORMAL",
    "DEMON",
    "STAR",
    "TIMELY",
    "TIMELY_DEMON",
    "TIMELY_STAR",
    "GAUNTLET",
    "GAUNTLET_DEMON",
    "GAUNTLET_STAR",
    "MAP_PACK",
    "QUEST",
    # prefixes
    "PREFIX",
    "prefix",
    # collected coins
    "VALUE_TO_COLLECTED_COINS",
    "NONE",
)

OFFICIAL = "n"
NORMAL = "c"
DEMON = "demon"
STAR = "star"
TIMELY = "d"
TIMELY_DEMON = TIMELY + DEMON  # aka weekly
TIMELY_STAR = TIMELY + STAR
GAUNTLET = "g"
GAUNTLET_DEMON = GAUNTLET + DEMON
GAUNTLET_STAR = GAUNTLET + STAR
MAP_PACK = "pack"
QUEST = "c"

ONE = str(1)

PREFIX = "{}_"
prefix = PREFIX.format

SUFFIX = "_{}"
suffix = SUFFIX.format

FIRST = 1
SECOND = 2
THIRD = 3

VALUE_TO_COLLECTED_COINS = {
    FIRST: CollectedCoins.FIRST,
    SECOND: CollectedCoins.SECOND,
    THIRD: CollectedCoins.THIRD,
}

NONE = CollectedCoins.NONE
