from typing import Dict

from attrs import define, field
from iters.iters import iter
from typing_aliases import StringDict, StringMapping
from typing_extensions import Self

from gd.api.database.common import NONE, ONE, VALUE_TO_COLLECTED_COINS
from gd.constants import (
    DEFAULT_ATTEMPTS,
    DEFAULT_DEMONS,
    DEFAULT_DESTROYED,
    DEFAULT_DIAMONDS,
    DEFAULT_JUMPS,
    DEFAULT_LEVELS,
    DEFAULT_LIKED,
    DEFAULT_MAP_PACKS,
    DEFAULT_ORBS,
    DEFAULT_RATED,
    DEFAULT_SECRET_COINS,
    DEFAULT_SHARDS,
    DEFAULT_STARS,
    DEFAULT_USER_COINS,
)
from gd.enums import CollectedCoins
from gd.models_utils import concat_name, parse_get_or, split_name

__all__ = ("Statistics",)

JUMPS = "1"
ATTEMPTS = "2"
OFFICIAL_LEVELS = "3"
NORMAL_LEVELS = "4"
DEMONS = "5"
STARS = "6"
MAP_PACKS = "7"
SECRET_COINS = "8"
DESTROYED = "9"
LIKED = "10"
RATED = "11"
USER_COINS = "12"
DIAMONDS = "13"
ORBS = "14"
TIMELY_LEVELS = "15"
FIRE_SHARDS = "16"
ICE_SHARDS = "17"
POISON_SHARDS = "18"
SHADOW_SHARDS = "19"
LAVA_SHARDS = "20"
BONUS_SHARDS = "21"
TOTAL_ORBS = "22"

DEFAULT_SCROLL_COIN = False
DEFAULT_VAULT_COIN = False
DEFAULT_CHAMBER_COIN = False

UNIQUE = "unique"


@define()
class Statistics:
    jumps: int = field(default=DEFAULT_JUMPS)
    attempts: int = field(default=DEFAULT_ATTEMPTS)
    official_levels: int = field(default=DEFAULT_LEVELS)
    normal_levels: int = field(default=DEFAULT_LEVELS)
    demons: int = field(default=DEFAULT_DEMONS)
    stars: int = field(default=DEFAULT_STARS)
    map_packs: int = field(default=DEFAULT_MAP_PACKS)
    secret_coins: int = field(default=DEFAULT_SECRET_COINS)
    destroyed: int = field(default=DEFAULT_DESTROYED)
    liked: int = field(default=DEFAULT_LIKED)
    rated: int = field(default=DEFAULT_RATED)
    user_coins: int = field(default=DEFAULT_USER_COINS)
    diamonds: int = field(default=DEFAULT_DIAMONDS)
    orbs: int = field(default=DEFAULT_ORBS)
    timely_levels: int = field(default=DEFAULT_LEVELS)
    fire_shards: int = field(default=DEFAULT_SHARDS)
    ice_shards: int = field(default=DEFAULT_SHARDS)
    poison_shards: int = field(default=DEFAULT_SHARDS)
    shadow_shards: int = field(default=DEFAULT_SHARDS)
    lava_shards: int = field(default=DEFAULT_SHARDS)
    bonus_shards: int = field(default=DEFAULT_SHARDS)
    total_orbs: int = field(default=DEFAULT_ORBS)

    scroll_coin: bool = field(default=DEFAULT_SCROLL_COIN)
    vault_coin: bool = field(default=DEFAULT_VAULT_COIN)
    chamber_coin: bool = field(default=DEFAULT_CHAMBER_COIN)

    official_coins: Dict[int, CollectedCoins] = field(factory=dict)

    @classmethod
    def from_robtop_data(cls, data: StringMapping[str]) -> Self:
        jumps = parse_get_or(int, DEFAULT_JUMPS, data.get(JUMPS))
        attempts = parse_get_or(int, DEFAULT_ATTEMPTS, data.get(ATTEMPTS))

        official_levels = parse_get_or(int, DEFAULT_LEVELS, data.get(OFFICIAL_LEVELS))
        normal_levels = parse_get_or(int, DEFAULT_LEVELS, data.get(NORMAL_LEVELS))

        demons = parse_get_or(int, DEFAULT_DEMONS, data.get(DEMONS))

        stars = parse_get_or(int, DEFAULT_STARS, data.get(STARS))

        map_packs = parse_get_or(int, DEFAULT_MAP_PACKS, data.get(MAP_PACKS))

        secret_coins = parse_get_or(int, DEFAULT_SECRET_COINS, data.get(SECRET_COINS))

        destroyed = parse_get_or(int, DEFAULT_DESTROYED, data.get(DESTROYED))

        liked = parse_get_or(int, DEFAULT_LIKED, data.get(LIKED))

        rated = parse_get_or(int, DEFAULT_RATED, data.get(RATED))

        user_coins = parse_get_or(int, DEFAULT_USER_COINS, data.get(USER_COINS))

        diamonds = parse_get_or(int, DEFAULT_DIAMONDS, data.get(DIAMONDS))

        orbs = parse_get_or(int, DEFAULT_ORBS, data.get(ORBS))

        timely_levels = parse_get_or(int, DEFAULT_LEVELS, data.get(TIMELY_LEVELS))

        fire_shards = parse_get_or(int, DEFAULT_SHARDS, data.get(FIRE_SHARDS))

        ice_shards = parse_get_or(int, DEFAULT_SHARDS, data.get(ICE_SHARDS))

        poison_shards = parse_get_or(int, DEFAULT_SHARDS, data.get(POISON_SHARDS))

        shadow_shards = parse_get_or(int, DEFAULT_SHARDS, data.get(SHADOW_SHARDS))

        lava_shards = parse_get_or(int, DEFAULT_SHARDS, data.get(LAVA_SHARDS))

        bonus_shards = parse_get_or(int, DEFAULT_SHARDS, data.get(BONUS_SHARDS))

        total_orbs = parse_get_or(int, DEFAULT_ORBS, data.get(TOTAL_ORBS))

        value_to_collected_coins = VALUE_TO_COLLECTED_COINS
        none = NONE

        official_coins: Dict[int, CollectedCoins] = {}

        for name in data.keys():
            try:
                level_id, value = iter(split_name(name)).skip(1).map(int).unwrap()  # skip `unique`

            except ValueError:
                pass

            else:
                if level_id not in official_coins:
                    official_coins[level_id] = none

                official_coins[level_id] |= value_to_collected_coins[value]

        return cls(
            jumps=jumps,
            attempts=attempts,
            official_levels=official_levels,
            normal_levels=normal_levels,
            demons=demons,
            stars=stars,
            map_packs=map_packs,
            secret_coins=secret_coins,
            destroyed=destroyed,
            liked=liked,
            rated=rated,
            user_coins=user_coins,
            diamonds=diamonds,
            orbs=orbs,
            timely_levels=timely_levels,
            fire_shards=fire_shards,
            ice_shards=ice_shards,
            poison_shards=poison_shards,
            shadow_shards=shadow_shards,
            lava_shards=lava_shards,
            bonus_shards=bonus_shards,
            total_orbs=total_orbs,
            official_coins=official_coins,
        )

    def to_robtop_data(self) -> StringDict[str]:
        data = {
            JUMPS: str(self.jumps),
            ATTEMPTS: str(self.attempts),
            OFFICIAL_LEVELS: str(self.official_levels),
            NORMAL_LEVELS: str(self.normal_levels),
            DEMONS: str(self.demons),
            STARS: str(self.stars),
            MAP_PACKS: str(self.map_packs),
            SECRET_COINS: str(self.secret_coins),
            DESTROYED: str(self.destroyed),
            LIKED: str(self.liked),
            RATED: str(self.rated),
            USER_COINS: str(self.user_coins),
            DIAMONDS: str(self.diamonds),
            ORBS: str(self.orbs),
            TIMELY_LEVELS: str(self.timely_levels),
            FIRE_SHARDS: str(self.fire_shards),
            ICE_SHARDS: str(self.ice_shards),
            POISON_SHARDS: str(self.poison_shards),
            SHADOW_SHARDS: str(self.shadow_shards),
            LAVA_SHARDS: str(self.lava_shards),
            BONUS_SHARDS: str(self.bonus_shards),
            TOTAL_ORBS: str(self.total_orbs),
        }

        value_to_collected_coins = VALUE_TO_COLLECTED_COINS
        unique = UNIQUE
        one = ONE

        for level_id, collected_coins in self.official_coins.items():
            for value, collected_coin in value_to_collected_coins.items():
                if collected_coins & collected_coin:
                    name = iter.of(unique, str(level_id), str(value)).collect(concat_name)

                    data[name] = one

        return data
