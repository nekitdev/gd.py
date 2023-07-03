from typing import Any, Dict, Tuple, Type, TypeVar

from attrs import define, field
from funcs.application import partial
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from pendulum import DateTime
from typing_aliases import StringDict, StringMapping

from gd.api.database.common import (
    GAUNTLET,
    MAP_PACK,
    NONE,
    ONE,
    QUEST,
    TIMELY,
    VALUE_TO_COLLECTED_COINS,
    prefix,
)
from gd.api.rewards import Quest, RewardItem
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_KEYS, WEEKLY_ID_ADD
from gd.date_time import utc_from_timestamp
from gd.enums import ByteOrder, ChestType, CollectedCoins
from gd.models_utils import concat_name, float_str, split_name
from gd.string_utils import remove_prefix, zero_pad

C = TypeVar("C", bound="Coins")


@define()
class Coins(Binary):
    normal: Dict[int, CollectedCoins] = field(factory=dict)
    gauntlet: Dict[int, CollectedCoins] = field(factory=dict)
    daily: Dict[int, CollectedCoins] = field(factory=dict)
    weekly: Dict[int, CollectedCoins] = field(factory=dict)

    @classmethod
    def from_binary(
        cls: Type[C],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> C:
        reader = Reader(binary, order)

        collected_coins = CollectedCoins

        read_u8 = reader.read_u8
        read_u16 = reader.read_u16
        read_u32 = reader.read_u32

        normal_length = read_u32()

        normal = {read_u32(): collected_coins(read_u8()) for _ in range(normal_length)}

        gauntlet_length = read_u16()

        gauntlet = {read_u32(): collected_coins(read_u8()) for _ in range(gauntlet_length)}

        daily_length = read_u16()

        daily = {read_u16(): collected_coins(read_u8()) for _ in range(daily_length)}

        weekly_length = read_u16()

        weekly = {read_u16(): collected_coins(read_u8()) for _ in range(weekly_length)}

        return cls(normal=normal, gauntlet=gauntlet, daily=daily, weekly=weekly)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        writer = Writer(binary, order)

        write_u8 = writer.write_u8
        write_u16 = writer.write_u16
        write_u32 = writer.write_u32

        normal = self.normal

        write_u32(len(normal))

        for level_id, collected_coins in normal.items():
            write_u32(level_id)
            write_u8(collected_coins.value)

        gauntlet = self.gauntlet

        write_u16(len(gauntlet))

        for level_id, collected_coins in gauntlet.items():
            write_u32(level_id)
            write_u8(collected_coins.value)

        daily = self.daily

        write_u16(len(daily))

        for daily_id, collected_coins in daily.items():
            write_u16(daily_id)
            write_u8(collected_coins.value)

        weekly = self.weekly

        write_u16(len(weekly))

        for weekly_id, collected_coins in weekly.items():
            write_u16(weekly_id)
            write_u8(collected_coins.value)

    @classmethod
    def from_robtop_data(
        cls: Type[C],
        data: StringMapping[str],
        daily_id_to_level_id: Dict[int, int],
        weekly_id_to_level_id: Dict[int, int],
    ) -> C:
        value_to_collected_coins = VALUE_TO_COLLECTED_COINS
        none = NONE

        normal: Dict[int, CollectedCoins] = {}
        gauntlet: Dict[int, CollectedCoins] = {}
        daily: Dict[int, CollectedCoins] = {}
        weekly: Dict[int, CollectedCoins] = {}

        weekly_id_add = WEEKLY_ID_ADD

        gauntlet_info = GAUNTLET

        for name in data.keys():
            splitted = split_name(name)

            try:
                level_id_string, value_string, info_string = splitted

            except ValueError:
                level_id, value = iter(splitted).map(int).tuple()

                if level_id not in normal:
                    normal[level_id] = none

                normal[level_id] |= value_to_collected_coins[value]

            else:
                level_id = int(level_id_string)

                value = int(value_string)

                if info_string == gauntlet_info:
                    if level_id not in gauntlet:
                        gauntlet[level_id] = none

                    gauntlet[level_id] |= value_to_collected_coins[value]

                else:
                    timely_id = int(info_string)

                    result, timely_id = divmod(timely_id, weekly_id_add)

                    if result:
                        weekly_id_to_level_id[timely_id] = level_id

                        timely = weekly

                    else:
                        daily_id_to_level_id[timely_id] = level_id

                        timely = daily

                    if timely_id not in timely:
                        timely[timely_id] = none

                    timely[timely_id] |= value_to_collected_coins[value]

        return cls(normal=normal, gauntlet=gauntlet, daily=daily, weekly=weekly)

    def to_robtop_data(
        self,
        daily_id_to_level_id: Dict[int, int],
        weekly_id_to_level_id: Dict[int, int],
    ) -> StringDict[str]:
        data: StringDict[str] = {}

        value_to_collected_coins = VALUE_TO_COLLECTED_COINS
        one = ONE

        for level_id, collected_coins in self.normal.items():
            for value, collected_coin in value_to_collected_coins.items():
                if collected_coins & collected_coin:
                    name = iter.of(level_id, value).map(str).collect(concat_name)

                    data[name] = one

        gauntlet = GAUNTLET

        for level_id, collected_coins in self.gauntlet.items():
            for value, collected_coin in value_to_collected_coins.items():
                if collected_coins & collected_coin:
                    name = iter.of(str(level_id), str(value), gauntlet).collect(concat_name)

                    data[name] = one

        for daily_id, collected_coins in self.daily.items():
            for value, collected_coin in value_to_collected_coins.items():
                if collected_coins & collected_coin:
                    level_id = daily_id_to_level_id[daily_id]

                    name = iter.of(level_id, value, daily_id).map(str).collect(concat_name)

                    data[name] = one

        for weekly_id, collected_coins in self.weekly.items():
            for value, collected_coin in value_to_collected_coins.items():
                if collected_coins & collected_coin:
                    level_id = weekly_id_to_level_id[weekly_id]

                    name = iter.of(level_id, value, weekly_id).map(str).collect(concat_name)

                    data[name] = one

        return data


QUESTS_LENGTH = 3

FIRST = 0
SECOND = 1

VERIFIED_COINS = "GS_3"
UNVERIFIED_COINS = "GS_4"
MAP_PACK_STARS = "GS_5"
PURCHASED_ITEMS = "GS_6"
NORMAL_RECORDS = "GS_7"
NORMAL_STARS = "GS_9"
OFFICIAL_RECORDS = "GS_10"
CHEST_REWARDS = "GS_11"
ACTIVE_QUESTS = "GS_12"
DIAMONDS = "GS_14"
UPCOMING_QUESTS = "GS_15"
TIMELY_RECORDS = "GS_16"
TIMELY_STARS = "GS_17"
GAUNTLET_RECORDS = "GS_18"
TREASURE_CHEST_REWARDS = "GS_19"
TOTAL_KEYS = "GS_20"
REWARDS = "GS_21"
AD_REWARDS = "GS_22"
NEW_GAUNTLET_RECORDS = "GS_23"
NEW_TIMELY_RECORDS = "GS_24"
WEEKLY_REWARDS = "GS_25"

MAP_PACK_PREFIX = prefix(MAP_PACK)
GAUNTLET_PREFIX = prefix(GAUNTLET)

OFFICIAL_REWARD_ALIGN = 4

S = TypeVar("S", bound="Storage")


@define()
class Storage(Binary):
    # keeping track of timely_id -> level_id relationships

    daily_id_to_level_id: Dict[int, int] = field(factory=dict)
    weekly_id_to_level_id: Dict[int, int] = field(factory=dict)

    # actual information

    verified_coins: Coins = field(factory=Coins)
    unverified_coins: Coins = field(factory=Coins)

    map_pack_stars: Dict[int, int] = field(factory=dict)

    purchased_items: Dict[int, int] = field(factory=dict)

    normal_records: Dict[int, int] = field(factory=dict)
    normal_stars: Dict[int, int] = field(factory=dict)

    official_records: Dict[int, int] = field(factory=dict)

    small_chest_rewards: Dict[int, RewardItem] = field(factory=dict)
    large_chest_rewards: Dict[int, RewardItem] = field(factory=dict)

    active_quests: OrderedSet[Quest] = field(factory=ordered_set)

    quest_diamonds: Dict[Tuple[int, int], int] = field(factory=dict)

    daily_diamonds: Dict[int, int] = field(factory=dict)

    upcoming_quests: OrderedSet[Quest] = field(factory=ordered_set)

    daily_records: Dict[int, int] = field(factory=dict)
    weekly_records: Dict[int, int] = field(factory=dict)

    daily_stars: Dict[int, int] = field(factory=dict)
    weekly_stars: Dict[int, int] = field(factory=dict)

    gauntlet_records: Dict[int, int] = field(factory=dict)

    treasure_chest_rewards: Dict[int, RewardItem] = field(factory=dict)

    total_keys: int = field(default=DEFAULT_KEYS)

    official_rewards: Dict[int, RewardItem] = field(factory=dict)
    gauntlet_rewards: Dict[int, RewardItem] = field(factory=dict)

    ad_rewards: Dict[DateTime, int] = field(factory=dict)

    new_gauntlet_records: Dict[int, int] = field(factory=dict)

    new_daily_records: Dict[int, int] = field(factory=dict)
    new_weekly_records: Dict[int, int] = field(factory=dict)

    weekly_rewards: Dict[int, RewardItem] = field(factory=dict)

    @classmethod
    def from_binary(
        cls: Type[S],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> S:
        reader = Reader(binary, order)

        read_u8 = reader.read_u8
        read_u16 = reader.read_u16
        read_u32 = reader.read_u32

        daily_id_to_level_id_length = read_u16()

        daily_id_to_level_id = {read_u16(): read_u32() for _ in range(daily_id_to_level_id_length)}

        weekly_id_to_level_id_length = read_u16()

        weekly_id_to_level_id = {
            read_u16(): read_u32() for _ in range(weekly_id_to_level_id_length)
        }

        unverified_coins = Coins.from_binary(binary, order, version)
        verified_coins = Coins.from_binary(binary, order, version)

        map_pack_stars_length = read_u16()

        map_pack_stars = {read_u16(): read_u8() for _ in range(map_pack_stars_length)}

        purchased_items_length = read_u16()

        purchased_items = {read_u16(): read_u16() for _ in range(purchased_items_length)}

        normal_records_length = read_u32()

        normal_records = {read_u32(): read_u8() for _ in range(normal_records_length)}

        normal_stars_length = read_u32()

        normal_stars = {read_u32(): read_u8() for _ in range(normal_stars_length)}

        official_records_length = read_u8()

        official_records = {read_u16(): read_u8() for _ in range(official_records_length)}

        reward_item_from_binary = partial(RewardItem.from_binary, binary, order, version)

        small_chest_rewards_length = read_u16()

        small_chest_rewards = {
            read_u16(): reward_item_from_binary() for _ in range(small_chest_rewards_length)
        }

        large_chest_rewards_length = read_u16()

        large_chest_rewards = {
            read_u16(): reward_item_from_binary() for _ in range(large_chest_rewards_length)
        }

        active_quests_length = read_u8()

        quest_from_binary = partial(Quest.from_binary, binary, order, version)

        active_quests = iter.repeat_exactly_with(
            quest_from_binary, active_quests_length
        ).ordered_set()

        quest_diamonds_length = read_u32()

        quest_diamonds = {(read_u8(), read_u16()): read_u8() for _ in range(quest_diamonds_length)}

        daily_diamonds_length = read_u16()

        daily_diamonds = {read_u16(): read_u8() for _ in range(daily_diamonds_length)}

        upcoming_quests_length = read_u8()

        upcoming_quests = iter.repeat_exactly_with(
            quest_from_binary, upcoming_quests_length
        ).ordered_set()

        daily_records_length = read_u16()

        daily_records = {read_u16(): read_u8() for _ in range(daily_records_length)}

        weekly_records_length = read_u16()

        weekly_records = {read_u16(): read_u8() for _ in range(weekly_records_length)}

        daily_stars_length = read_u16()

        daily_stars = {read_u16(): read_u8() for _ in range(daily_stars_length)}

        weekly_stars_length = read_u16()

        weekly_stars = {read_u16(): read_u8() for _ in range(weekly_stars_length)}

        gauntlet_records_length = read_u16()

        gauntlet_records = {read_u32(): read_u8() for _ in range(gauntlet_records_length)}

        treasure_chest_rewards_length = read_u16()

        treasure_chest_rewards = {
            read_u16(): reward_item_from_binary() for _ in range(treasure_chest_rewards_length)
        }

        total_keys = read_u16()

        official_rewards_length = read_u8()

        official_rewards = {
            read_u8(): reward_item_from_binary() for _ in range(official_rewards_length)
        }

        gauntlet_rewards_length = read_u16()

        gauntlet_rewards = {
            read_u16(): reward_item_from_binary() for _ in range(gauntlet_rewards_length)
        }

        read_f64 = reader.read_f64

        ad_rewards_length = read_u16()

        ad_rewards = {utc_from_timestamp(read_f64()): read_u16() for _ in range(ad_rewards_length)}

        new_gauntlet_records_length = read_u16()

        new_gauntlet_records = {read_u32(): read_u8() for _ in range(new_gauntlet_records_length)}

        new_daily_records_length = read_u16()

        new_daily_records = {read_u16(): read_u8() for _ in range(new_daily_records_length)}

        new_weekly_records_length = read_u16()

        new_weekly_records = {read_u16(): read_u8() for _ in range(new_weekly_records_length)}

        weekly_rewards_length = read_u16()

        weekly_rewards = {
            read_u16(): reward_item_from_binary() for _ in range(weekly_rewards_length)
        }

        return cls(
            daily_id_to_level_id=daily_id_to_level_id,
            weekly_id_to_level_id=weekly_id_to_level_id,
            unverified_coins=unverified_coins,
            verified_coins=verified_coins,
            map_pack_stars=map_pack_stars,
            purchased_items=purchased_items,
            normal_records=normal_records,
            normal_stars=normal_stars,
            official_records=official_records,
            small_chest_rewards=small_chest_rewards,
            large_chest_rewards=large_chest_rewards,
            active_quests=active_quests,
            quest_diamonds=quest_diamonds,
            daily_diamonds=daily_diamonds,
            upcoming_quests=upcoming_quests,
            daily_records=daily_records,
            weekly_records=weekly_records,
            daily_stars=daily_stars,
            weekly_stars=weekly_stars,
            gauntlet_records=gauntlet_records,
            treasure_chest_rewards=treasure_chest_rewards,
            total_keys=total_keys,
            official_rewards=official_rewards,
            gauntlet_rewards=gauntlet_rewards,
            ad_rewards=ad_rewards,
            new_gauntlet_records=new_gauntlet_records,
            new_daily_records=new_daily_records,
            new_weekly_records=new_weekly_records,
            weekly_rewards=weekly_rewards,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        write_u8 = writer.write_u8
        write_u16 = writer.write_u16
        write_u32 = writer.write_u32

        daily_id_to_level_id = self.daily_id_to_level_id

        write_u16(len(daily_id_to_level_id))

        for daily_id, level_id in daily_id_to_level_id.items():
            write_u16(daily_id)
            write_u32(level_id)

        weekly_id_to_level_id = self.weekly_id_to_level_id

        write_u16(len(weekly_id_to_level_id))

        for weekly_id, level_id in weekly_id_to_level_id.items():
            write_u16(weekly_id)
            write_u32(level_id)

        self.unverified_coins.to_binary(binary, order, version)
        self.verified_coins.to_binary(binary, order, version)

        map_pack_stars = self.map_pack_stars

        write_u16(len(map_pack_stars))

        for map_pack_id, stars in map_pack_stars.items():
            write_u16(map_pack_id)
            write_u8(stars)

        purchased_items = self.purchased_items

        write_u16(len(purchased_items))

        for item_id, price in purchased_items.items():
            write_u16(item_id)
            write_u16(price)

        normal_records = self.normal_records

        write_u32(len(normal_records))

        for level_id, record in normal_records.items():
            write_u32(level_id)
            write_u8(record)

        normal_stars = self.normal_stars

        write_u32(len(normal_stars))

        for level_id, stars in normal_stars.items():
            write_u32(level_id)
            write_u8(stars)

        official_records = self.official_records

        write_u8(len(official_records))

        for level_id, record in official_records.items():
            write_u16(level_id)
            write_u8(record)

        small_chest_rewards = self.small_chest_rewards

        write_u16(len(small_chest_rewards))

        for chest_id, reward_item in small_chest_rewards.items():
            write_u16(chest_id)
            reward_item.to_binary(binary, order, version)

        large_chest_rewards = self.large_chest_rewards

        write_u16(len(large_chest_rewards))

        for chest_id, reward_item in large_chest_rewards.items():
            write_u16(chest_id)
            reward_item.to_binary(binary, order, version)

        active_quests = self.active_quests

        write_u8(len(active_quests))

        for quest in active_quests:
            quest.to_binary(binary, order, version)

        quest_diamonds = self.quest_diamonds

        write_u32(len(quest_diamonds))

        for (quest_order, count), diamonds in quest_diamonds.items():
            write_u8(quest_order)
            write_u16(count)
            write_u8(diamonds)

        daily_diamonds = self.daily_diamonds

        write_u16(len(daily_diamonds))

        for daily_id, diamonds in daily_diamonds.items():
            write_u16(daily_id)
            write_u8(diamonds)

        upcoming_quests = self.upcoming_quests

        write_u8(len(upcoming_quests))

        for quest in upcoming_quests:
            quest.to_binary(binary, order, version)

        daily_records = self.daily_records

        write_u16(len(daily_records))

        for daily_id, record in daily_records.items():
            write_u16(daily_id)
            write_u8(record)

        weekly_records = self.weekly_records

        write_u16(len(weekly_records))

        for weekly_id, record in weekly_records.items():
            write_u16(weekly_id)
            write_u8(record)

        daily_stars = self.daily_stars

        write_u16(len(daily_stars))

        for daily_id, stars in daily_stars.items():
            write_u16(daily_id)
            write_u8(stars)

        weekly_stars = self.weekly_stars

        write_u16(len(weekly_stars))

        for weekly_id, stars in weekly_stars.items():
            write_u16(weekly_id)
            write_u8(stars)

        gauntlet_records = self.gauntlet_records

        write_u16(len(gauntlet_records))

        for level_id, record in gauntlet_records.items():
            write_u32(level_id)
            write_u8(record)

        treasure_chest_rewards = self.treasure_chest_rewards

        write_u16(len(treasure_chest_rewards))

        for chest_id, reward_item in treasure_chest_rewards.items():
            write_u16(chest_id)
            reward_item.to_binary(binary, order, version)

        write_u16(self.total_keys)

        official_rewards = self.official_rewards

        write_u8(len(official_rewards))

        for official_reward_id, reward_item in official_rewards.items():
            write_u8(official_reward_id)
            reward_item.to_binary(binary, order, version)

        gauntlet_rewards = self.gauntlet_rewards

        write_u16(len(gauntlet_rewards))

        for gauntlet_id, reward_item in gauntlet_rewards.items():
            write_u16(gauntlet_id)
            reward_item.to_binary(binary, order, version)

        write_f64 = writer.write_f64

        ad_rewards = self.ad_rewards

        write_u16(len(ad_rewards))

        for rewarded_at, orbs in ad_rewards.items():
            timestamp = rewarded_at.timestamp()  # type: ignore

            write_f64(timestamp)
            write_u16(orbs)

        new_gauntlet_records = self.new_gauntlet_records

        write_u16(len(new_gauntlet_records))

        for level_id, record in new_gauntlet_records.items():
            write_u32(level_id)
            write_u8(record)

        new_daily_records = self.new_daily_records

        write_u16(len(new_daily_records))

        for daily_id, record in new_daily_records.items():
            write_u16(daily_id)
            write_u8(record)

        new_weekly_records = self.new_weekly_records

        write_u16(len(new_weekly_records))

        for weekly_id, record in new_weekly_records.items():
            write_u16(weekly_id)
            write_u8(record)

        weekly_rewards = self.weekly_rewards

        write_u16(len(weekly_rewards))

        for weekly_id, reward_item in weekly_rewards.items():
            write_u16(weekly_id)
            reward_item.to_binary(binary, order, version)

    @classmethod
    def from_robtop_data(cls: Type[S], data: StringMapping[Any]) -> S:  # type: ignore
        daily_id_to_level_id: Dict[int, int] = {}
        weekly_id_to_level_id: Dict[int, int] = {}

        verified_coins_data = data.get(VERIFIED_COINS, {})

        verified_coins = Coins.from_robtop_data(
            verified_coins_data, daily_id_to_level_id, weekly_id_to_level_id
        )

        unverified_coins_data = data.get(UNVERIFIED_COINS, {})

        unverified_coins = Coins.from_robtop_data(
            unverified_coins_data, daily_id_to_level_id, weekly_id_to_level_id
        )

        map_pack_prefix = MAP_PACK_PREFIX

        map_pack_stars_data = data.get(MAP_PACK_STARS, {})

        map_pack_stars = {
            int(remove_prefix(name, map_pack_prefix)): int(string)
            for name, string in map_pack_stars_data.items()
        }

        purchased_items_data = data.get(PURCHASED_ITEMS, {})

        purchased_items = {
            int(item_id_string): int(price_string)
            for item_id_string, price_string in purchased_items_data.items()
        }

        normal_records_data = data.get(NORMAL_RECORDS, {})

        normal_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in normal_records_data.items()
        }

        normal_stars_data = data.get(NORMAL_STARS, {})

        normal_stars = {
            int(level_id_string): int(stars_string)
            for level_id_string, stars_string in normal_stars_data.items()
        }

        official_records_data = data.get(OFFICIAL_RECORDS, {})

        official_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in official_records_data.items()
        }

        chest_rewards_data = data.get(CHEST_REWARDS, {})

        small_chest_rewards: Dict[int, RewardItem] = {}
        large_chest_rewards: Dict[int, RewardItem] = {}

        reward_item_type = RewardItem

        for name, reward_item_data in chest_rewards_data.items():
            chest_type_value, chest_id = iter(split_name(name)).map(int).tuple()

            chest_type = ChestType(chest_type_value)

            reward_item = reward_item_type.from_robtop_data(reward_item_data)

            if chest_type.is_small():
                small_chest_rewards[chest_id] = reward_item

            if chest_type.is_large():
                large_chest_rewards[chest_id] = reward_item

        quest_type = Quest

        active_quests_data = data.get(ACTIVE_QUESTS, {})

        active_quests = (
            iter(active_quests_data.values()).map(quest_type.from_robtop_data).ordered_set()
        )

        quest = QUEST
        daily = TIMELY

        first = FIRST
        second = SECOND

        diamonds_data = data.get(DIAMONDS, {})

        quest_diamonds: Dict[Tuple[int, int], int] = {}
        daily_diamonds: Dict[int, int] = {}

        for name, diamonds_string in diamonds_data.items():
            diamonds = int(diamonds_string)

            string, value = name[first], name[second:]

            if string == daily:
                daily_id = int(value)

                daily_diamonds[daily_id] = diamonds

            if string == quest:
                quest_order, count = iter.of(value[first], value[second:]).map(int).tuple()

                quest_diamonds[quest_order, count] = diamonds

        upcoming_quests_data = data.get(UPCOMING_QUESTS, {})

        upcoming_quests = (
            iter(upcoming_quests_data.values()).map(quest_type.from_robtop_data).ordered_set()
        )

        weekly_id_add = WEEKLY_ID_ADD

        timely_records_data = data.get(TIMELY_RECORDS, {})

        daily_records: Dict[int, int] = {}
        weekly_records: Dict[int, int] = {}

        for timely_id_string, record_string in timely_records_data.items():
            timely_id = int(timely_id_string)
            record = int(record_string)

            result, timely_id = divmod(timely_id, weekly_id_add)

            if result:
                weekly_records[timely_id] = record

            else:
                daily_records[timely_id] = record

        timely_stars_data = data.get(TIMELY_STARS, {})

        daily_stars: Dict[int, int] = {}
        weekly_stars: Dict[int, int] = {}

        for timely_id_string, stars_string in timely_stars_data.items():
            timely_id = int(timely_id_string)

            stars = int(stars_string)

            result, timely_id = divmod(timely_id, weekly_id_add)

            if result:
                weekly_stars[timely_id] = stars

            else:
                daily_stars[timely_id] = stars

        gauntlet_records_data = data.get(GAUNTLET_RECORDS, {})

        gauntlet_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in gauntlet_records_data.items()
        }

        treasure_chest_rewards_data = data.get(TREASURE_CHEST_REWARDS, {})

        treasure_chest_rewards = {
            int(chest_id_string): reward_item_type.from_robtop_data(reward_item_data)
            for chest_id_string, reward_item_data in treasure_chest_rewards_data.items()
        }

        total_keys = data.get(TOTAL_KEYS, DEFAULT_KEYS)

        gauntlet_prefix = GAUNTLET_PREFIX

        rewards_data = data.get(REWARDS, {})

        official_rewards: Dict[int, RewardItem] = {}
        gauntlet_rewards: Dict[int, RewardItem] = {}

        for name, reward_item_data in rewards_data.items():
            string = remove_prefix(name, gauntlet_prefix)

            value = int(string)

            reward_item = reward_item_type.from_robtop_data(reward_item_data)

            if name == string:
                official_rewards[value] = reward_item

            else:
                gauntlet_rewards[value] = reward_item

        ad_rewards_data = data.get(AD_REWARDS, {})

        ad_rewards = {
            utc_from_timestamp(float(timestamp_string)): int(orbs_string)
            for timestamp_string, orbs_string in ad_rewards_data.items()
        }

        new_gauntlet_records_data = data.get(NEW_GAUNTLET_RECORDS, {})

        new_gauntlet_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in new_gauntlet_records_data.items()
        }

        new_timely_records_data = data.get(NEW_TIMELY_RECORDS, {})

        new_daily_records: Dict[int, int] = {}
        new_weekly_records: Dict[int, int] = {}

        for timely_id_string, record_string in new_timely_records_data.items():
            timely_id = int(timely_id_string)

            record = int(record_string)

            result, timely_id = divmod(timely_id, weekly_id_add)

            if result:
                new_weekly_records[timely_id] = record

            else:
                new_daily_records[timely_id] = record

        weekly = TIMELY

        weekly_rewards_data = data.get(WEEKLY_REWARDS, {})

        weekly_rewards = {
            int(remove_prefix(name, weekly))
            % weekly_id_add: reward_item_type.from_robtop_data(reward_item_data)
            for name, reward_item_data in weekly_rewards_data.items()
        }

        return cls(
            daily_id_to_level_id=daily_id_to_level_id,
            weekly_id_to_level_id=weekly_id_to_level_id,
            verified_coins=verified_coins,
            unverified_coins=unverified_coins,
            map_pack_stars=map_pack_stars,
            purchased_items=purchased_items,
            normal_records=normal_records,
            normal_stars=normal_stars,
            official_records=official_records,
            small_chest_rewards=small_chest_rewards,
            large_chest_rewards=large_chest_rewards,
            active_quests=active_quests,
            quest_diamonds=quest_diamonds,
            daily_diamonds=daily_diamonds,
            upcoming_quests=upcoming_quests,
            daily_records=daily_records,
            weekly_records=weekly_records,
            daily_stars=daily_stars,
            weekly_stars=weekly_stars,
            gauntlet_records=gauntlet_records,
            treasure_chest_rewards=treasure_chest_rewards,
            total_keys=total_keys,
            official_rewards=official_rewards,
            gauntlet_rewards=gauntlet_rewards,
            ad_rewards=ad_rewards,
            new_gauntlet_records=new_gauntlet_records,
            new_daily_records=new_daily_records,
            new_weekly_records=new_weekly_records,
            weekly_rewards=weekly_rewards,
        )

    def to_robtop_data(self) -> StringDict[Any]:
        daily_id_to_level_id = self.daily_id_to_level_id
        weekly_id_to_level_id = self.weekly_id_to_level_id

        verified_coins_data = self.verified_coins.to_robtop_data(
            daily_id_to_level_id,
            weekly_id_to_level_id,
        )

        unverified_coins_data = self.unverified_coins.to_robtop_data(
            daily_id_to_level_id,
            weekly_id_to_level_id,
        )

        map_pack_prefix = MAP_PACK_PREFIX

        map_pack_stars_data = {
            map_pack_prefix + str(map_pack_id): str(map_pack_stars)
            for map_pack_id, map_pack_stars in self.map_pack_stars.items()
        }

        purchased_items_data = {
            str(item_id): str(price) for item_id, price in self.purchased_items.items()
        }

        normal_records_data = {
            str(level_id): str(record) for level_id, record in self.normal_records.items()
        }

        normal_stars_data = {
            str(level_id): str(stars) for level_id, stars in self.normal_stars.items()
        }

        official_records_data = {
            str(level_id): str(record) for level_id, record in self.official_records.items()
        }

        small = ChestType.SMALL.value

        small_chest_rewards_data = {
            iter.of(small, chest_id).map(str).collect(concat_name): reward_item.to_robtop_data()
            for chest_id, reward_item in self.small_chest_rewards.items()
        }

        large = ChestType.LARGE.value

        large_chest_rewards_data = {
            iter.of(large, chest_id).map(str).collect(concat_name): reward_item.to_robtop_data()
            for chest_id, reward_item in self.large_chest_rewards.items()
        }

        chest_rewards_data: StringDict[Any] = {}

        chest_rewards_data.update(small_chest_rewards_data)
        chest_rewards_data.update(large_chest_rewards_data)

        active_quests_data = {
            str(quest.quest_order): quest.to_robtop_data() for quest in self.active_quests
        }

        quest = QUEST
        daily = TIMELY

        quest_diamonds_data = {
            quest + str(quest_order) + str(count): str(diamonds)
            for (quest_order, count), diamonds in self.quest_diamonds.items()
        }

        daily_diamonds_data = {
            daily + str(daily_id): str(diamonds)
            for daily_id, diamonds in self.daily_diamonds.items()
        }

        diamonds_data: StringDict[str] = {}

        diamonds_data.update(quest_diamonds_data)
        diamonds_data.update(daily_diamonds_data)

        upcoming_quests_data = {
            str(quest.quest_order): quest.to_robtop_data() for quest in self.upcoming_quests
        }

        weekly_id_add = WEEKLY_ID_ADD

        daily_records_data = {
            str(daily_id): str(record) for daily_id, record in self.daily_records.items()
        }

        weekly_records_data = {
            str(weekly_id + weekly_id_add): str(record)
            for weekly_id, record in self.weekly_records.items()
        }

        timely_records_data: StringDict[str] = {}

        timely_records_data.update(daily_records_data)
        timely_records_data.update(weekly_records_data)

        daily_stars_data = {
            str(daily_id): str(stars) for daily_id, stars in self.daily_stars.items()
        }

        weekly_stars_data = {
            str(weekly_id + weekly_id_add): str(stars)
            for weekly_id, stars in self.weekly_stars.items()
        }

        timely_stars_data: StringDict[str] = {}

        timely_stars_data.update(daily_stars_data)
        timely_stars_data.update(weekly_stars_data)

        gauntlet_records_data = {
            str(level_id): str(record) for level_id, record in self.gauntlet_records.items()
        }

        treasure_chest_rewards_data = {
            str(chest_id): reward_item.to_robtop_data()
            for chest_id, reward_item in self.treasure_chest_rewards.items()
        }

        total_keys = self.total_keys

        official_reward_align = OFFICIAL_REWARD_ALIGN

        official_rewards_data = {
            zero_pad(official_reward_align, official_reward_id): reward_item.to_robtop_data()
            for official_reward_id, reward_item in self.official_rewards.items()
        }

        gauntlet_prefix = GAUNTLET_PREFIX

        gauntlet_rewards_data = {
            gauntlet_prefix + str(gauntlet_id): reward_item.to_robtop_data()
            for gauntlet_id, reward_item in self.gauntlet_rewards.items()
        }

        rewards_data: StringDict[Any] = {}

        rewards_data.update(official_rewards_data)
        rewards_data.update(gauntlet_rewards_data)

        ad_rewards_data = {
            float_str(rewarded_at.timestamp()): str(orbs)  # type: ignore
            for rewarded_at, orbs in self.ad_rewards.items()
        }

        new_gauntlet_records_data = {
            str(level_id): str(record) for level_id, record in self.new_gauntlet_records.items()
        }

        new_daily_records_data = {
            str(daily_id): str(record) for daily_id, record in self.new_daily_records.items()
        }

        new_weekly_records_data = {
            str(weekly_id + weekly_id_add): str(record)
            for weekly_id, record in self.new_weekly_records.items()
        }

        new_timely_records_data: StringDict[str] = {}

        new_timely_records_data.update(new_daily_records_data)
        new_timely_records_data.update(new_weekly_records_data)

        weekly = TIMELY

        weekly_rewards_data = {
            weekly + str(weekly_id + weekly_id_add): reward_item.to_robtop_data()
            for weekly_id, reward_item in self.weekly_rewards.items()
        }

        data: StringDict[Any] = {
            VERIFIED_COINS: verified_coins_data,
            UNVERIFIED_COINS: unverified_coins_data,
            MAP_PACK_STARS: map_pack_stars_data,
            PURCHASED_ITEMS: purchased_items_data,
            NORMAL_RECORDS: normal_records_data,
            NORMAL_STARS: normal_stars_data,
            OFFICIAL_RECORDS: official_records_data,
            CHEST_REWARDS: chest_rewards_data,
            ACTIVE_QUESTS: active_quests_data,
            DIAMONDS: diamonds_data,
            UPCOMING_QUESTS: upcoming_quests_data,
            TIMELY_RECORDS: timely_records_data,
            TIMELY_STARS: timely_stars_data,
            GAUNTLET_RECORDS: gauntlet_records_data,
            TREASURE_CHEST_REWARDS: treasure_chest_rewards_data,
            TOTAL_KEYS: total_keys,
            REWARDS: rewards_data,
            AD_REWARDS: ad_rewards_data,
            NEW_GAUNTLET_RECORDS: new_gauntlet_records_data,
            NEW_TIMELY_RECORDS: new_timely_records_data,
            WEEKLY_REWARDS: weekly_rewards_data,
        }

        return data
