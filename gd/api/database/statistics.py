from typing import Dict

from attrs import define, field
from iters.iters import iter
from typing_aliases import StringDict
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
    DEFAULT_MOONS,
    DEFAULT_ORBS,
    DEFAULT_RATED,
    DEFAULT_SECRET_COINS,
    DEFAULT_SHARDS,
    DEFAULT_STARS,
    DEFAULT_USER_COINS,
)
from gd.enums import CollectedCoins
from gd.models_utils import concat_name, int_bool, split_name
from gd.robtop_view import StringRobTopView

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
EARTH_SHARDS = "23"
BLOOD_SHARDS = "24"
METAL_SHARDS = "25"
LIGHT_SHARDS = "26"
SOUL_SHARDS = "27"
MOONS = "28"

SCROLL_COIN = "secret04"
VAULT_COIN = "secret06"
CHAMBER_COIN = "secretB03"

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
    earth_shards: int = field(default=DEFAULT_SHARDS)
    blood_shards: int = field(default=DEFAULT_SHARDS)
    metal_shards: int = field(default=DEFAULT_SHARDS)
    light_shards: int = field(default=DEFAULT_SHARDS)
    soul_shards: int = field(default=DEFAULT_SHARDS)
    moons: int = field(default=DEFAULT_ORBS)

    scroll_coin: bool = field(default=DEFAULT_SCROLL_COIN)
    vault_coin: bool = field(default=DEFAULT_VAULT_COIN)
    chamber_coin: bool = field(default=DEFAULT_CHAMBER_COIN)

    official_coins: Dict[int, CollectedCoins] = field(factory=dict)

    def has_scroll_coin(self) -> bool:
        return self.scroll_coin

    def has_vault_coin(self) -> bool:
        return self.vault_coin

    def has_chamber_coin(self) -> bool:
        return self.chamber_coin

    @classmethod
    def from_robtop_view(cls, view: StringRobTopView[str]) -> Self:
        jumps = view.get_option(JUMPS).map(int).unwrap_or(DEFAULT_JUMPS)
        attempts = view.get_option(ATTEMPTS).map(int).unwrap_or(DEFAULT_ATTEMPTS)

        official_levels = view.get_option(OFFICIAL_LEVELS).map(int).unwrap_or(DEFAULT_LEVELS)
        normal_levels = view.get_option(NORMAL_LEVELS).map(int).unwrap_or(DEFAULT_LEVELS)

        demons = view.get_option(DEMONS).map(int).unwrap_or(DEFAULT_DEMONS)

        stars = view.get_option(STARS).map(int).unwrap_or(DEFAULT_STARS)

        map_packs = view.get_option(MAP_PACKS).map(int).unwrap_or(DEFAULT_MAP_PACKS)

        secret_coins = view.get_option(SECRET_COINS).map(int).unwrap_or(DEFAULT_SECRET_COINS)

        destroyed = view.get_option(DESTROYED).map(int).unwrap_or(DEFAULT_DESTROYED)

        liked = view.get_option(LIKED).map(int).unwrap_or(DEFAULT_LIKED)

        rated = view.get_option(RATED).map(int).unwrap_or(DEFAULT_RATED)

        user_coins = view.get_option(USER_COINS).map(int).unwrap_or(DEFAULT_USER_COINS)

        diamonds = view.get_option(DIAMONDS).map(int).unwrap_or(DEFAULT_DIAMONDS)

        orbs = view.get_option(ORBS).map(int).unwrap_or(DEFAULT_ORBS)

        timely_levels = view.get_option(TIMELY_LEVELS).map(int).unwrap_or(DEFAULT_LEVELS)

        fire_shards = view.get_option(FIRE_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        ice_shards = view.get_option(ICE_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        poison_shards = view.get_option(POISON_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        shadow_shards = view.get_option(SHADOW_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        lava_shards = view.get_option(LAVA_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        bonus_shards = view.get_option(BONUS_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)

        total_orbs = view.get_option(TOTAL_ORBS).map(int).unwrap_or(DEFAULT_ORBS)

        earth_shards = view.get_option(EARTH_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        blood_shards = view.get_option(BLOOD_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        metal_shards = view.get_option(METAL_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        light_shards = view.get_option(LIGHT_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)
        soul_shards = view.get_option(SOUL_SHARDS).map(int).unwrap_or(DEFAULT_SHARDS)

        moons = view.get_option(MOONS).map(int).unwrap_or(DEFAULT_MOONS)

        scroll_coin = view.get_option(SCROLL_COIN).map(int_bool).unwrap_or(DEFAULT_SCROLL_COIN)
        vault_coin = view.get_option(VAULT_COIN).map(int_bool).unwrap_or(DEFAULT_VAULT_COIN)
        chamber_coin = view.get_option(CHAMBER_COIN).map(int_bool).unwrap_or(DEFAULT_CHAMBER_COIN)

        value_to_collected_coins = VALUE_TO_COLLECTED_COINS
        none = NONE

        official_coins: Dict[int, CollectedCoins] = {}

        for name in view.mapping:
            try:
                level_id, value = iter(split_name(name)).skip(1).map(int).tuple()  # skip `unique`

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
            earth_shards=earth_shards,
            blood_shards=blood_shards,
            metal_shards=metal_shards,
            light_shards=light_shards,
            soul_shards=soul_shards,
            moons=moons,
            scroll_coin=scroll_coin,
            vault_coin=vault_coin,
            chamber_coin=chamber_coin,
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
            EARTH_SHARDS: str(self.earth_shards),
            BLOOD_SHARDS: str(self.blood_shards),
            METAL_SHARDS: str(self.metal_shards),
            LIGHT_SHARDS: str(self.light_shards),
            SOUL_SHARDS: str(self.soul_shards),
            MOONS: str(self.moons),
        }

        value_to_collected_coins = VALUE_TO_COLLECTED_COINS
        unique = UNIQUE
        one = ONE

        if self.has_scroll_coin():
            name = iter.of(unique, SCROLL_COIN).collect(concat_name)

            data[name] = one

        if self.has_vault_coin():
            name = iter.of(unique, VAULT_COIN).collect(concat_name)

            data[name] = one

        if self.has_chamber_coin():
            name = iter.of(unique, CHAMBER_COIN).collect(concat_name)

            data[name] = one

        for level_id, collected_coins in self.official_coins.items():
            for value, collected_coin in value_to_collected_coins.items():
                if collected_coins & collected_coin:
                    name = iter.of(unique, str(level_id), str(value)).collect(concat_name)

                    data[name] = one

        return data
