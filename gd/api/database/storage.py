from typing import Any, Dict, Tuple

from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from pendulum import DateTime
from typing_aliases import StringDict
from typing_extensions import Self

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
from gd.constants import DEFAULT_KEYS, WEEKLY_ID_ADD
from gd.date_time import utc_from_timestamp
from gd.enums import ChestType, CollectedCoins
from gd.models_utils import concat_name, float_str, split_name
from gd.robtop_view import RobTopView, StringRobTopView
from gd.string_utils import remove_prefix, zero_pad


@define()
class Coins:
    normal: Dict[int, CollectedCoins] = field(factory=dict)
    gauntlet: Dict[int, CollectedCoins] = field(factory=dict)
    daily: Dict[int, CollectedCoins] = field(factory=dict)
    weekly: Dict[int, CollectedCoins] = field(factory=dict)

    @classmethod
    def from_robtop_view(
        cls,
        view: StringRobTopView[str],
        daily_id_to_level_id: Dict[int, int],
        weekly_id_to_level_id: Dict[int, int],
    ) -> Self:
        value_to_collected_coins = VALUE_TO_COLLECTED_COINS
        none = NONE

        normal: Dict[int, CollectedCoins] = {}
        gauntlet: Dict[int, CollectedCoins] = {}
        daily: Dict[int, CollectedCoins] = {}
        weekly: Dict[int, CollectedCoins] = {}

        weekly_id_add = WEEKLY_ID_ADD

        gauntlet_info = GAUNTLET

        for name in view.mapping:
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


@define()
class Storage:
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
    def from_robtop_view(cls, view: StringRobTopView[Any]) -> Self:
        daily_id_to_level_id: Dict[int, int] = {}
        weekly_id_to_level_id: Dict[int, int] = {}

        verified_coins_data: StringDict[str] = view.get_option(VERIFIED_COINS).unwrap_or_else(dict)

        verified_coins_view = RobTopView(verified_coins_data)

        verified_coins = Coins.from_robtop_view(
            verified_coins_view, daily_id_to_level_id, weekly_id_to_level_id
        )

        unverified_coins_data: StringDict[str] = view.get_option(UNVERIFIED_COINS).unwrap_or_else(
            dict
        )

        unverified_coins_view = RobTopView(unverified_coins_data)

        unverified_coins = Coins.from_robtop_view(
            unverified_coins_view, daily_id_to_level_id, weekly_id_to_level_id
        )

        map_pack_prefix = MAP_PACK_PREFIX

        map_pack_stars_data: StringDict[str] = view.get_option(MAP_PACK_STARS).unwrap_or_else(dict)

        map_pack_stars_view = RobTopView(map_pack_stars_data)

        map_pack_stars = {
            int(remove_prefix(name, map_pack_prefix)): int(string)
            for name, string in map_pack_stars_view.mapping.items()
        }

        purchased_items_data: StringDict[str] = view.get_option(PURCHASED_ITEMS).unwrap_or_else(
            dict
        )

        purchased_items_view = RobTopView(purchased_items_data)

        purchased_items = {
            int(item_id_string): int(price_string)
            for item_id_string, price_string in purchased_items_view.mapping.items()
        }

        normal_records_data: StringDict[str] = view.get_option(NORMAL_RECORDS).unwrap_or_else(dict)

        normal_records_view = RobTopView(normal_records_data)

        normal_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in normal_records_view.mapping.items()
        }

        normal_stars_data: StringDict[str] = view.get_option(NORMAL_STARS).unwrap_or_else(dict)

        normal_stars_view = RobTopView(normal_stars_data)

        normal_stars = {
            int(level_id_string): int(stars_string)
            for level_id_string, stars_string in normal_stars_view.mapping.items()
        }

        official_records_data: StringDict[str] = view.get_option(OFFICIAL_RECORDS).unwrap_or_else(
            dict
        )

        official_records_view = RobTopView(official_records_data)

        official_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in official_records_view.mapping.items()
        }

        chest_rewards_data: StringDict[Any] = view.get_option(CHEST_REWARDS).unwrap_or_else(
            dict
        )  # TODO: here

        chest_rewards_view = RobTopView(chest_rewards_data)

        small_chest_rewards: Dict[int, RewardItem] = {}
        large_chest_rewards: Dict[int, RewardItem] = {}

        for name, reward_item_data in chest_rewards_view.mapping.items():
            reward_item_view = RobTopView(reward_item_data)

            chest_type_value, chest_id = iter(split_name(name)).map(int).tuple()

            chest_type = ChestType(chest_type_value)

            reward_item = RewardItem.from_robtop_view(reward_item_view)

            if chest_type.is_small():
                small_chest_rewards[chest_id] = reward_item

            if chest_type.is_large():
                large_chest_rewards[chest_id] = reward_item

        active_quests_data: StringDict[Any] = view.get_option(ACTIVE_QUESTS).unwrap_or_else(dict)

        active_quests_view = RobTopView(active_quests_data)

        active_quests = (
            iter(active_quests_view.mapping.values())
            .map(RobTopView)
            .map(Quest.from_robtop_view)
            .ordered_set()
        )

        quest = QUEST
        daily = TIMELY

        first = FIRST
        second = SECOND

        diamonds_data: StringDict[str] = view.get_option(DIAMONDS).unwrap_or_else(dict)

        diamonds_view = RobTopView(diamonds_data)

        quest_diamonds: Dict[Tuple[int, int], int] = {}
        daily_diamonds: Dict[int, int] = {}

        for name, diamonds_string in diamonds_view.mapping.items():
            diamonds = int(diamonds_string)

            string, value = name[first], name[second:]

            if string == daily:
                daily_id = int(value)

                daily_diamonds[daily_id] = diamonds

            if string == quest:
                quest_order, count = iter.of(value[first], value[second:]).map(int).tuple()

                quest_diamonds[quest_order, count] = diamonds

        upcoming_quests_data: StringDict[Any] = view.get_option(UPCOMING_QUESTS).unwrap_or_else(
            dict
        )

        upcoming_quests_view = RobTopView(upcoming_quests_data)

        upcoming_quests = (
            iter(upcoming_quests_view.mapping.values()).map(Quest.from_robtop_view).ordered_set()
        )

        weekly_id_add = WEEKLY_ID_ADD

        timely_records_data: StringDict[str] = view.get_option(TIMELY_RECORDS).unwrap_or_else(dict)

        timely_records_view = RobTopView(timely_records_data)

        daily_records: Dict[int, int] = {}
        weekly_records: Dict[int, int] = {}

        for timely_id_string, record_string in timely_records_view.mapping.items():
            timely_id = int(timely_id_string)
            record = int(record_string)

            result, timely_id = divmod(timely_id, weekly_id_add)

            if result:
                weekly_records[timely_id] = record

            else:
                daily_records[timely_id] = record

        timely_stars_data: StringDict[str] = view.get_option(TIMELY_STARS).unwrap_or_else(dict)

        timely_stars_view = RobTopView(timely_stars_data)

        daily_stars: Dict[int, int] = {}
        weekly_stars: Dict[int, int] = {}

        for timely_id_string, stars_string in timely_stars_view.mapping.items():
            timely_id = int(timely_id_string)

            stars = int(stars_string)

            result, timely_id = divmod(timely_id, weekly_id_add)

            if result:
                weekly_stars[timely_id] = stars

            else:
                daily_stars[timely_id] = stars

        gauntlet_records_data: StringDict[str] = view.get_option(GAUNTLET_RECORDS).unwrap_or_else(
            dict
        )

        gauntlet_records_view = RobTopView(gauntlet_records_data)

        gauntlet_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in gauntlet_records_view.mapping.items()
        }

        treasure_chest_rewards_data: StringDict[Any] = view.get_option(
            TREASURE_CHEST_REWARDS
        ).unwrap_or_else(dict)

        treasure_chest_rewards_view = RobTopView(treasure_chest_rewards_data)

        treasure_chest_rewards = {
            int(chest_id_string): RewardItem.from_robtop_view(RobTopView(reward_item_data))
            for chest_id_string, reward_item_data in treasure_chest_rewards_view.mapping.items()
        }

        total_keys = view.get_option(TOTAL_KEYS).unwrap_or(DEFAULT_KEYS)

        gauntlet_prefix = GAUNTLET_PREFIX

        rewards_data: StringDict[Any] = view.get_option(REWARDS).unwrap_or_else(dict)

        rewards_view = RobTopView(rewards_data)

        official_rewards: Dict[int, RewardItem] = {}
        gauntlet_rewards: Dict[int, RewardItem] = {}

        for name, reward_item_data in rewards_view.mapping.items():
            reward_item_view = RobTopView(reward_item_data)

            string = remove_prefix(name, gauntlet_prefix)

            id = int(string)

            reward_item = RewardItem.from_robtop_view(reward_item_view)

            if name == string:
                official_rewards[id] = reward_item

            else:
                gauntlet_rewards[id] = reward_item

        ad_rewards_data: StringDict[str] = view.get_option(AD_REWARDS).unwrap_or_else(dict)

        ad_rewards_view = RobTopView(ad_rewards_data)

        ad_rewards = {
            utc_from_timestamp(float(timestamp_string)): int(orbs_string)
            for timestamp_string, orbs_string in ad_rewards_view.mapping.items()
        }

        new_gauntlet_records_data: StringDict[str] = view.get_option(
            NEW_GAUNTLET_RECORDS
        ).unwrap_or_else(dict)

        new_gauntlet_records_view = RobTopView(new_gauntlet_records_data)

        new_gauntlet_records = {
            int(level_id_string): int(record_string)
            for level_id_string, record_string in new_gauntlet_records_view.mapping.items()
        }

        new_timely_records_data: StringDict[str] = view.get_option(
            NEW_TIMELY_RECORDS
        ).unwrap_or_else(dict)

        new_timely_records_view = RobTopView(new_timely_records_data)

        new_daily_records: Dict[int, int] = {}
        new_weekly_records: Dict[int, int] = {}

        for timely_id_string, record_string in new_timely_records_view.mapping.items():
            timely_id = int(timely_id_string)

            record = int(record_string)

            result, timely_id = divmod(timely_id, weekly_id_add)

            if result:
                new_weekly_records[timely_id] = record

            else:
                new_daily_records[timely_id] = record

        weekly = TIMELY

        weekly_rewards_data: StringDict[Any] = view.get_option(WEEKLY_REWARDS).unwrap_or_else(dict)

        weekly_rewards_view = RobTopView(weekly_rewards_data)

        weekly_rewards = {
            int(remove_prefix(name, weekly)) % weekly_id_add: RewardItem.from_robtop_view(
                RobTopView(reward_item_data)
            )
            for name, reward_item_data in weekly_rewards_view.mapping.items()
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
            str(quest.order): quest.to_robtop_data() for quest in self.active_quests
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
            str(quest.order): quest.to_robtop_data() for quest in self.upcoming_quests
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
            float_str(rewarded_at.timestamp()): str(orbs)
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
