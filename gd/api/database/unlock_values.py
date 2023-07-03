from typing import Type, TypeVar

from attrs import define
from typing_aliases import StringDict, StringMapping

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder
from gd.models_utils import bool_str, int_bool, parse_get_or

__all__ = ("UnlockValues",)

THE_CHALLENGE_UNLOCKED = "ugv_1"
GUBFLUB_HINT_1 = "ugv_2"
GUBFLUB_HINT_2 = "ugv_3"
THE_CHALLENGE_COMPLETED = "ugv_4"
TREASURE_ROOM_UNLOCKED = "ugv_5"
CHAMBER_OF_TIME_UNLOCKED = "ugv_6"
CHAMBER_OF_TIME_DISCOVERED = "ugv_7"
MASTER_EMBLEM_SHOWN = "ugv_8"
GATE_KEEPER_DIALOG = "ugv_9"
SCRATCH_DIALOG = "ugv_10"
SECRET_SHOP_UNLOCKED = "ugv_11"
DEMON_GUARDIAN_DIALOG = "ugv_12"
DEMON_FREED = "ugv_13"
DEMON_KEY_1 = "ugv_14"
DEMON_KEY_2 = "ugv_15"
DEMON_KEY_3 = "ugv_16"
SHOP_KEEPER_DIALOG = "ugv_17"
WORLD_ONLINE_LEVELS = "ugv_18"
DEMON_DISCOVERED = "ugv_19"
COMMUNITY_SHOP_UNLOCKED = "ugv_20"
POTBOR_DIALOG = "ugv_21"
YOUTUBE_CHEST_UNLOCKED = "ugv_22"
FACEBOOK_CHEST_UNLOCKED = "ugv_23"
TWITTER_CHEST_UNLOCKED = "ugv_24"
# FIREBIRD_GATE_KEEPER = "ugv_25"
# TWITCH_CHEST_UNLOCKED_BIT = "ugv_26"
# DISCORD_CHEST_UNLOCKED_BIT = "ugv_27"

THE_CHALLENGE_UNLOCKED_BIT = 0b1
GUBFLUB_HINT_1_BIT = 0b10
GUBFLUB_HINT_2_BIT = 0b100
THE_CHALLENGE_COMPLETED_BIT = 0b1000
TREASURE_ROOM_UNLOCKED_BIT = 0b10000
CHAMBER_OF_TIME_UNLOCKED_BIT = 0b100000
CHAMBER_OF_TIME_DISCOVERED_BIT = 0b1000000
MASTER_EMBLEM_SHOWN_BIT = 0b10000000
GATE_KEEPER_DIALOG_BIT = 0b1_00000000
SCRATCH_DIALOG_BIT = 0b10_00000000
SECRET_SHOP_UNLOCKED_BIT = 0b100_00000000
DEMON_GUARDIAN_DIALOG_BIT = 0b1000_00000000
DEMON_FREED_BIT = 0b10000_00000000
DEMON_KEY_1_BIT = 0b100000_00000000
DEMON_KEY_2_BIT = 0b1000000_00000000
DEMON_KEY_3_BIT = 0b10000000_00000000
SHOP_KEEPER_DIALOG_BIT = 0b1_00000000_00000000
WORLD_ONLINE_LEVELS_BIT = 0b10_00000000_00000000
DEMON_DISCOVERED_BIT = 0b100_00000000_00000000
COMMUNITY_SHOP_UNLOCKED_BIT = 0b1000_00000000_00000000
POTBOR_DIALOG_BIT = 0b10000_00000000_00000000
YOUTUBE_CHEST_UNLOCKED_BIT = 0b100000_00000000_00000000
FACEBOOK_CHEST_UNLOCKED_BIT = 0b1000000_00000000_00000000
TWITTER_CHEST_UNLOCKED_BIT = 0b10000000_00000000_00000000
# FIREBIRD_GATE_KEEPER_BIT = 0b1_00000000_00000000_00000000
# TWITCH_CHEST_UNLOCKED_BIT = 0b10_00000000_00000000_00000000
# DISCORD_CHEST_UNLOCKED_BIT = 0b100_00000000_00000000_00000000


DEFAULT_THE_CHALLENGE_UNLOCKED = False
DEFAULT_GUBFLUB_HINT_1 = False
DEFAULT_GUBFLUB_HINT_2 = False
DEFAULT_THE_CHALLENGE_COMPLETED = False
DEFAULT_TREASURE_ROOM_UNLOCKED = False
DEFAULT_CHAMBER_OF_TIME_UNLOCKED = False
DEFAULT_CHAMBER_OF_TIME_DISCOVERED = False
DEFAULT_MASTER_EMBLEM_SHOWN = False
DEFAULT_GATE_KEEPER_DIALOG = False
DEFAULT_SCRATCH_DIALOG = False
DEFAULT_SECRET_SHOP_UNLOCKED = False
DEFAULT_DEMON_GUARDIAN_DIALOG = False
DEFAULT_DEMON_FREED = False
DEFAULT_DEMON_KEY_1 = False
DEFAULT_DEMON_KEY_2 = False
DEFAULT_DEMON_KEY_3 = False
DEFAULT_SHOP_KEEPER_DIALOG = False
DEFAULT_WORLD_ONLINE_LEVELS = False
DEFAULT_DEMON_DISCOVERED = False
DEFAULT_COMMUNITY_SHOP_UNLOCKED = False
DEFAULT_POTBOR_DIALOG = False
DEFAULT_YOUTUBE_CHEST_UNLOCKED = False
DEFAULT_FACEBOOK_CHEST_UNLOCKED = False
DEFAULT_TWITTER_CHEST_UNLOCKED = False
# DEFAULT_FIREBIRD_GATE_KEEPER = False
# DEFAULT_TWITCH_CHEST_UNLOCKED = False
# DEFAULT_DISCORD_CHEST_UNLOCKED = False


UV = TypeVar("UV", bound="UnlockValues")


@define()
class UnlockValues(Binary):
    the_challenge_unlocked: bool = DEFAULT_THE_CHALLENGE_UNLOCKED
    gubflub_hint_1: bool = DEFAULT_GUBFLUB_HINT_1
    gubflub_hint_2: bool = DEFAULT_GUBFLUB_HINT_2
    the_challenge_completed: bool = DEFAULT_THE_CHALLENGE_COMPLETED
    treasure_room_unlocked: bool = DEFAULT_TREASURE_ROOM_UNLOCKED
    chamber_of_time_unlocked: bool = DEFAULT_CHAMBER_OF_TIME_UNLOCKED
    chamber_of_time_discovered: bool = DEFAULT_CHAMBER_OF_TIME_DISCOVERED
    master_emblem_shown: bool = DEFAULT_MASTER_EMBLEM_SHOWN
    gate_keeper_dialog: bool = DEFAULT_GATE_KEEPER_DIALOG
    scratch_dialog: bool = DEFAULT_SCRATCH_DIALOG
    secret_shop_unlocked: bool = DEFAULT_SECRET_SHOP_UNLOCKED
    demon_guardian_dialog: bool = DEFAULT_DEMON_GUARDIAN_DIALOG
    demon_freed: bool = DEFAULT_DEMON_FREED
    demon_key_1: bool = DEFAULT_DEMON_KEY_1
    demon_key_2: bool = DEFAULT_DEMON_KEY_2
    demon_key_3: bool = DEFAULT_DEMON_KEY_3
    shop_keeper_dialog: bool = DEFAULT_SHOP_KEEPER_DIALOG
    world_online_levels: bool = DEFAULT_WORLD_ONLINE_LEVELS
    demon_discovered: bool = DEFAULT_DEMON_DISCOVERED
    community_shop_unlocked: bool = DEFAULT_COMMUNITY_SHOP_UNLOCKED
    potbor_dialog: bool = DEFAULT_POTBOR_DIALOG
    youtube_chest_unlocked: bool = DEFAULT_YOUTUBE_CHEST_UNLOCKED
    facebook_chest_unlocked: bool = DEFAULT_FACEBOOK_CHEST_UNLOCKED
    twitter_chest_unlocked: bool = DEFAULT_TWITTER_CHEST_UNLOCKED
    # firebird_gate_keeper: bool = DEFAULT_FIREBIRD_GATE_KEEPER
    # twitch_chest_unlocked: bool = DEFAULT_TWITCH_CHEST_UNLOCKED
    # discord_chest_unlocked: bool = DEFAULT_DISCORD_CHEST_UNLOCKED

    @classmethod
    def from_binary(
        cls: Type[UV],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> UV:
        reader = Reader(binary, order)

        the_challenge_unlocked_bit = THE_CHALLENGE_UNLOCKED_BIT
        gubflub_hint_1_bit = GUBFLUB_HINT_1_BIT
        gubflub_hint_2_bit = GUBFLUB_HINT_2_BIT
        the_challenge_completed_bit = THE_CHALLENGE_COMPLETED_BIT
        treasure_room_unlocked_bit = TREASURE_ROOM_UNLOCKED_BIT
        chamber_of_time_unlocked_bit = CHAMBER_OF_TIME_UNLOCKED_BIT
        chamber_of_time_discovered_bit = CHAMBER_OF_TIME_DISCOVERED_BIT
        master_emblem_shown_bit = MASTER_EMBLEM_SHOWN_BIT
        gate_keeper_dialog_bit = GATE_KEEPER_DIALOG_BIT
        scratch_dialog_bit = SCRATCH_DIALOG_BIT
        secret_shop_unlocked_bit = SECRET_SHOP_UNLOCKED_BIT
        demon_guardian_dialog_bit = DEMON_GUARDIAN_DIALOG_BIT
        demon_freed_bit = DEMON_FREED_BIT
        demon_key_1_bit = DEMON_KEY_1_BIT
        demon_key_2_bit = DEMON_KEY_2_BIT
        demon_key_3_bit = DEMON_KEY_3_BIT
        shop_keeper_dialog_bit = SHOP_KEEPER_DIALOG_BIT
        world_online_levels_bit = WORLD_ONLINE_LEVELS_BIT
        demon_discovered_bit = DEMON_DISCOVERED_BIT
        community_shop_unlocked_bit = COMMUNITY_SHOP_UNLOCKED_BIT
        potbor_dialog_bit = POTBOR_DIALOG_BIT
        youtube_chest_unlocked_bit = YOUTUBE_CHEST_UNLOCKED_BIT
        facebook_chest_unlocked_bit = FACEBOOK_CHEST_UNLOCKED_BIT
        twitter_chest_unlocked_bit = TWITTER_CHEST_UNLOCKED_BIT
        # firebird_gate_keeper_bit = FIREBIRD_GATE_KEEPER_BIT
        # twitch_chest_unlocked_bit = TWITCH_CHEST_UNLOCKED_BIT
        # discord_chest_unlocked_bit = DISCORD_CHEST_UNLOCKED_BIT

        value = reader.read_u64()

        the_challenge_unlocked = value & the_challenge_unlocked_bit == the_challenge_unlocked_bit
        gubflub_hint_1 = value & gubflub_hint_1_bit == gubflub_hint_1_bit
        gubflub_hint_2 = value & gubflub_hint_2_bit == gubflub_hint_2_bit
        the_challenge_completed = value & the_challenge_completed_bit == the_challenge_completed_bit
        treasure_room_unlocked = value & treasure_room_unlocked_bit == treasure_room_unlocked_bit
        chamber_of_time_unlocked = (
            value & chamber_of_time_unlocked_bit == chamber_of_time_unlocked_bit
        )
        chamber_of_time_discovered = (
            value & chamber_of_time_discovered_bit == chamber_of_time_discovered_bit
        )
        master_emblem_shown = value & master_emblem_shown_bit == master_emblem_shown_bit
        gate_keeper_dialog = value & gate_keeper_dialog_bit == gate_keeper_dialog_bit
        scratch_dialog = value & scratch_dialog_bit == scratch_dialog_bit
        secret_shop_unlocked = value & secret_shop_unlocked_bit == secret_shop_unlocked_bit
        demon_guardian_dialog = value & demon_guardian_dialog_bit == demon_guardian_dialog_bit
        demon_freed = value & demon_freed_bit == demon_freed_bit
        demon_key_1 = value & demon_key_1_bit == demon_key_1_bit
        demon_key_2 = value & demon_key_2_bit == demon_key_2_bit
        demon_key_3 = value & demon_key_3_bit == demon_key_3_bit
        shop_keeper_dialog = value & shop_keeper_dialog_bit == shop_keeper_dialog_bit
        world_online_levels = value & world_online_levels_bit == world_online_levels_bit
        demon_discovered = value & demon_discovered_bit == demon_discovered_bit
        community_shop_unlocked = value & community_shop_unlocked_bit == community_shop_unlocked_bit
        potbor_dialog = value & potbor_dialog_bit == potbor_dialog_bit
        youtube_chest_unlocked = value & youtube_chest_unlocked_bit == youtube_chest_unlocked_bit
        facebook_chest_unlocked = value & facebook_chest_unlocked_bit == facebook_chest_unlocked_bit
        twitter_chest_unlocked = value & twitter_chest_unlocked_bit == twitter_chest_unlocked_bit
        # firebird_gate_keeper = value & firebird_gate_keeper_bit == firebird_gate_keeper_bit
        # twitch_chest_unlocked = value & twitch_chest_unlocked_bit == twitch_chest_unlocked_bit
        # discord_chest_unlocked = value & discord_chest_unlocked_bit == discord_chest_unlocked_bit

        return cls(
            the_challenge_unlocked=the_challenge_unlocked,
            gubflub_hint_1=gubflub_hint_1,
            gubflub_hint_2=gubflub_hint_2,
            the_challenge_completed=the_challenge_completed,
            treasure_room_unlocked=treasure_room_unlocked,
            chamber_of_time_unlocked=chamber_of_time_unlocked,
            chamber_of_time_discovered=chamber_of_time_discovered,
            master_emblem_shown=master_emblem_shown,
            gate_keeper_dialog=gate_keeper_dialog,
            scratch_dialog=scratch_dialog,
            secret_shop_unlocked=secret_shop_unlocked,
            demon_guardian_dialog=demon_guardian_dialog,
            demon_freed=demon_freed,
            demon_key_1=demon_key_1,
            demon_key_2=demon_key_2,
            demon_key_3=demon_key_3,
            shop_keeper_dialog=shop_keeper_dialog,
            world_online_levels=world_online_levels,
            demon_discovered=demon_discovered,
            community_shop_unlocked=community_shop_unlocked,
            potbor_dialog=potbor_dialog,
            youtube_chest_unlocked=youtube_chest_unlocked,
            facebook_chest_unlocked=facebook_chest_unlocked,
            twitter_chest_unlocked=twitter_chest_unlocked,
            # firebird_gate_keeper=firebird_gate_keeper,
            # twitch_chest_unlocked=twitch_chest_unlocked,
            # discord_chest_unlocked=discord_chest_unlocked,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        value = 0

        if self.is_the_challenge_unlocked():
            value |= THE_CHALLENGE_UNLOCKED_BIT

        if self.is_gubflub_hint_1():
            value |= GUBFLUB_HINT_1_BIT

        if self.is_gubflub_hint_2():
            value |= GUBFLUB_HINT_2_BIT

        if self.is_the_challenge_completed():
            value |= THE_CHALLENGE_COMPLETED_BIT

        if self.is_treasure_room_unlocked():
            value |= TREASURE_ROOM_UNLOCKED_BIT

        if self.is_chamber_of_time_unlocked():
            value |= CHAMBER_OF_TIME_UNLOCKED_BIT

        if self.is_chamber_of_time_discovered():
            value |= CHAMBER_OF_TIME_DISCOVERED_BIT

        if self.is_master_emblem_shown():
            value |= MASTER_EMBLEM_SHOWN_BIT

        if self.is_gate_keeper_dialog():
            value |= GATE_KEEPER_DIALOG_BIT

        if self.is_scratch_dialog():
            value |= SCRATCH_DIALOG_BIT

        if self.is_secret_shop_unlocked():
            value |= SECRET_SHOP_UNLOCKED_BIT

        if self.is_demon_guardian_dialog():
            value |= DEMON_GUARDIAN_DIALOG_BIT

        if self.is_demon_freed():
            value |= DEMON_FREED_BIT

        if self.is_demon_key_1():
            value |= DEMON_KEY_1_BIT

        if self.is_demon_key_2():
            value |= DEMON_KEY_2_BIT

        if self.is_demon_key_3():
            value |= DEMON_KEY_3_BIT

        if self.is_shop_keeper_dialog():
            value |= SHOP_KEEPER_DIALOG_BIT

        if self.is_world_online_levels():
            value |= WORLD_ONLINE_LEVELS_BIT

        if self.is_demon_discovered():
            value |= DEMON_DISCOVERED_BIT

        if self.is_community_shop_unlocked():
            value |= COMMUNITY_SHOP_UNLOCKED_BIT

        if self.is_potbor_dialog():
            value |= POTBOR_DIALOG_BIT

        if self.is_youtube_chest_unlocked():
            value |= YOUTUBE_CHEST_UNLOCKED_BIT

        if self.is_facebook_chest_unlocked():
            value |= FACEBOOK_CHEST_UNLOCKED_BIT

        if self.is_twitter_chest_unlocked():
            value |= TWITTER_CHEST_UNLOCKED_BIT

        # if self.is_firebird_gate_keeper():
        #     value |= FIREBIRD_GATE_KEEPER_BIT

        # if self.is_twitch_chest_unlocked():
        #     value |= TWITCH_CHEST_UNLOCKED_BIT

        # if self.is_discord_chest_unlocked():
        #     value |= DISCORD_CHEST_UNLOCKED_BIT

        writer.write_u64(value)

    @classmethod
    def from_robtop_data(cls: Type[UV], data: StringMapping[str]) -> UV:  # type: ignore
        the_challenge_unlocked = parse_get_or(
            int_bool, DEFAULT_THE_CHALLENGE_UNLOCKED, data.get(THE_CHALLENGE_UNLOCKED)
        )
        gubflub_hint_1 = parse_get_or(int_bool, DEFAULT_GUBFLUB_HINT_1, data.get(GUBFLUB_HINT_1))
        gubflub_hint_2 = parse_get_or(int_bool, DEFAULT_GUBFLUB_HINT_2, data.get(GUBFLUB_HINT_2))
        the_challenge_completed = parse_get_or(
            int_bool, DEFAULT_THE_CHALLENGE_COMPLETED, data.get(THE_CHALLENGE_COMPLETED)
        )
        treasure_room_unlocked = parse_get_or(
            int_bool, DEFAULT_TREASURE_ROOM_UNLOCKED, data.get(TREASURE_ROOM_UNLOCKED)
        )
        chamber_of_time_unlocked = parse_get_or(
            int_bool, DEFAULT_CHAMBER_OF_TIME_UNLOCKED, data.get(CHAMBER_OF_TIME_UNLOCKED)
        )
        chamber_of_time_discovered = parse_get_or(
            int_bool, DEFAULT_CHAMBER_OF_TIME_DISCOVERED, data.get(CHAMBER_OF_TIME_DISCOVERED)
        )
        master_emblem_shown = parse_get_or(
            int_bool, DEFAULT_MASTER_EMBLEM_SHOWN, data.get(MASTER_EMBLEM_SHOWN)
        )
        gate_keeper_dialog = parse_get_or(
            int_bool, DEFAULT_GATE_KEEPER_DIALOG, data.get(GATE_KEEPER_DIALOG)
        )
        scratch_dialog = parse_get_or(int_bool, DEFAULT_SCRATCH_DIALOG, data.get(SCRATCH_DIALOG))
        secret_shop_unlocked = parse_get_or(
            int_bool, DEFAULT_SECRET_SHOP_UNLOCKED, data.get(SECRET_SHOP_UNLOCKED)
        )
        demon_guardian_dialog = parse_get_or(
            int_bool, DEFAULT_DEMON_GUARDIAN_DIALOG, data.get(DEMON_GUARDIAN_DIALOG)
        )
        demon_freed = parse_get_or(int_bool, DEFAULT_DEMON_FREED, data.get(DEMON_FREED))
        demon_key_1 = parse_get_or(int_bool, DEFAULT_DEMON_KEY_1, data.get(DEMON_KEY_1))
        demon_key_2 = parse_get_or(int_bool, DEFAULT_DEMON_KEY_2, data.get(DEMON_KEY_2))
        demon_key_3 = parse_get_or(int_bool, DEFAULT_DEMON_KEY_3, data.get(DEMON_KEY_3))
        shop_keeper_dialog = parse_get_or(
            int_bool, DEFAULT_SHOP_KEEPER_DIALOG, data.get(SHOP_KEEPER_DIALOG)
        )
        world_online_levels = parse_get_or(
            int_bool, DEFAULT_WORLD_ONLINE_LEVELS, data.get(WORLD_ONLINE_LEVELS)
        )
        demon_discovered = parse_get_or(
            int_bool, DEFAULT_DEMON_DISCOVERED, data.get(DEMON_DISCOVERED)
        )
        community_shop_unlocked = parse_get_or(
            int_bool, DEFAULT_COMMUNITY_SHOP_UNLOCKED, data.get(COMMUNITY_SHOP_UNLOCKED)
        )
        potbor_dialog = parse_get_or(int_bool, DEFAULT_POTBOR_DIALOG, data.get(POTBOR_DIALOG))
        youtube_chest_unlocked = parse_get_or(
            int_bool, DEFAULT_YOUTUBE_CHEST_UNLOCKED, data.get(YOUTUBE_CHEST_UNLOCKED)
        )
        facebook_chest_unlocked = parse_get_or(
            int_bool, DEFAULT_FACEBOOK_CHEST_UNLOCKED, data.get(FACEBOOK_CHEST_UNLOCKED)
        )
        twitter_chest_unlocked = parse_get_or(
            int_bool, DEFAULT_TWITTER_CHEST_UNLOCKED, data.get(TWITTER_CHEST_UNLOCKED)
        )
        # firebird_gate_keeper = parse_get_or(
        #     int_bool, DEFAULT_FIREBIRD_GATE_KEEPER, data.get(FIREBIRD_GATE_KEEPER)
        # )
        # twitch_chest_unlocked = parse_get_or(
        #     int_bool, DEFAULT_TWITCH_CHEST_UNLOCKED, data.get(TWITCH_CHEST_UNLOCKED)
        # )
        # discord_chest_unlocked = parse_get_or(
        #     int_bool, DEFAULT_DISCORD_CHEST_UNLOCKED, data.get(DISCORD_CHEST_UNLOCKED)
        # )

        return cls(
            the_challenge_unlocked=the_challenge_unlocked,
            gubflub_hint_1=gubflub_hint_1,
            gubflub_hint_2=gubflub_hint_2,
            the_challenge_completed=the_challenge_completed,
            treasure_room_unlocked=treasure_room_unlocked,
            chamber_of_time_unlocked=chamber_of_time_unlocked,
            chamber_of_time_discovered=chamber_of_time_discovered,
            master_emblem_shown=master_emblem_shown,
            gate_keeper_dialog=gate_keeper_dialog,
            scratch_dialog=scratch_dialog,
            secret_shop_unlocked=secret_shop_unlocked,
            demon_guardian_dialog=demon_guardian_dialog,
            demon_freed=demon_freed,
            demon_key_1=demon_key_1,
            demon_key_2=demon_key_2,
            demon_key_3=demon_key_3,
            shop_keeper_dialog=shop_keeper_dialog,
            world_online_levels=world_online_levels,
            demon_discovered=demon_discovered,
            community_shop_unlocked=community_shop_unlocked,
            potbor_dialog=potbor_dialog,
            youtube_chest_unlocked=youtube_chest_unlocked,
            facebook_chest_unlocked=facebook_chest_unlocked,
            twitter_chest_unlocked=twitter_chest_unlocked,
            # firebird_gate_keeper=firebird_gate_keeper,
            # twitch_chest_unlocked=twitch_chest_unlocked,
            # discord_chest_unlocked=discord_chest_unlocked,
        )

    def to_robtop_data(self) -> StringDict[str]:
        data: StringDict[str] = {}

        the_challenge_unlocked = self.is_the_challenge_unlocked()

        if the_challenge_unlocked:
            data[THE_CHALLENGE_UNLOCKED] = bool_str(the_challenge_unlocked)

        gubflub_hint_1 = self.is_gubflub_hint_1()

        if gubflub_hint_1:
            data[GUBFLUB_HINT_1] = bool_str(gubflub_hint_1)

        gubflub_hint_2 = self.is_gubflub_hint_2()

        if gubflub_hint_2:
            data[GUBFLUB_HINT_2] = bool_str(gubflub_hint_2)

        the_challenge_completed = self.is_the_challenge_completed()

        if the_challenge_completed:
            data[THE_CHALLENGE_COMPLETED] = bool_str(the_challenge_completed)

        treasure_room_unlocked = self.is_treasure_room_unlocked()

        if treasure_room_unlocked:
            data[TREASURE_ROOM_UNLOCKED] = bool_str(treasure_room_unlocked)

        chamber_of_time_unlocked = self.is_chamber_of_time_unlocked()

        if chamber_of_time_unlocked:
            data[CHAMBER_OF_TIME_UNLOCKED] = bool_str(chamber_of_time_unlocked)

        chamber_of_time_discovered = self.is_chamber_of_time_discovered()

        if chamber_of_time_discovered:
            data[CHAMBER_OF_TIME_DISCOVERED] = bool_str(chamber_of_time_discovered)

        master_emblem_shown = self.is_master_emblem_shown()

        if master_emblem_shown:
            data[MASTER_EMBLEM_SHOWN] = bool_str(master_emblem_shown)

        gate_keeper_dialog = self.is_gate_keeper_dialog()

        if gate_keeper_dialog:
            data[GATE_KEEPER_DIALOG] = bool_str(gate_keeper_dialog)

        scratch_dialog = self.is_scratch_dialog()

        if scratch_dialog:
            data[SCRATCH_DIALOG] = bool_str(scratch_dialog)

        secret_shop_unlocked = self.is_secret_shop_unlocked()

        if secret_shop_unlocked:
            data[SECRET_SHOP_UNLOCKED] = bool_str(secret_shop_unlocked)

        demon_guardian_dialog = self.is_demon_guardian_dialog()

        if demon_guardian_dialog:
            data[DEMON_GUARDIAN_DIALOG] = bool_str(demon_guardian_dialog)

        demon_freed = self.is_demon_freed()

        if demon_freed:
            data[DEMON_FREED] = bool_str(demon_freed)

        demon_key_1 = self.is_demon_key_1()

        if demon_key_1:
            data[DEMON_KEY_1] = bool_str(demon_key_1)

        demon_key_2 = self.is_demon_key_2()

        if demon_key_2:
            data[DEMON_KEY_2] = bool_str(demon_key_2)

        demon_key_3 = self.is_demon_key_3()

        if demon_key_3:
            data[DEMON_KEY_3] = bool_str(demon_key_3)

        shop_keeper_dialog = self.is_shop_keeper_dialog()

        if shop_keeper_dialog:
            data[SHOP_KEEPER_DIALOG] = bool_str(shop_keeper_dialog)

        world_online_levels = self.is_world_online_levels()

        if world_online_levels:
            data[WORLD_ONLINE_LEVELS] = bool_str(world_online_levels)

        demon_discovered = self.is_demon_discovered()

        if demon_discovered:
            data[DEMON_DISCOVERED] = bool_str(demon_discovered)

        community_shop_unlocked = self.is_community_shop_unlocked()

        if community_shop_unlocked:
            data[COMMUNITY_SHOP_UNLOCKED] = bool_str(community_shop_unlocked)

        potbor_dialog = self.is_potbor_dialog()

        if potbor_dialog:
            data[POTBOR_DIALOG] = bool_str(potbor_dialog)

        youtube_chest_unlocked = self.is_youtube_chest_unlocked()

        if youtube_chest_unlocked:
            data[YOUTUBE_CHEST_UNLOCKED] = bool_str(youtube_chest_unlocked)

        facebook_chest_unlocked = self.is_facebook_chest_unlocked()

        if facebook_chest_unlocked:
            data[FACEBOOK_CHEST_UNLOCKED] = bool_str(facebook_chest_unlocked)

        twitter_chest_unlocked = self.is_twitter_chest_unlocked()

        if twitter_chest_unlocked:
            data[TWITTER_CHEST_UNLOCKED] = bool_str(twitter_chest_unlocked)

        # firebird_gate_keeper = self.is_firebird_gate_keeper()

        # if firebird_gate_keeper:
        #     data[FIREBIRD_GATE_KEEPER] = bool_str(firebird_gate_keeper)

        # twitch_chest_unlocked = self.is_twitch_chest_unlocked()

        # if twitch_chest_unlocked:
        #     data[TWITCH_CHEST_UNLOCKED] = bool_str(twitch_chest_unlocked)

        # discord_chest_unlocked = self.is_discord_chest_unlocked()

        # if discord_chest_unlocked:
        #     data[DISCORD_CHEST_UNLOCKED] = bool_str(discord_chest_unlocked)

        return data

    def is_the_challenge_unlocked(self) -> bool:
        return self.the_challenge_unlocked

    def is_gubflub_hint_1(self) -> bool:
        return self.gubflub_hint_1

    def is_gubflub_hint_2(self) -> bool:
        return self.gubflub_hint_2

    def is_the_challenge_completed(self) -> bool:
        return self.the_challenge_completed

    def is_treasure_room_unlocked(self) -> bool:
        return self.treasure_room_unlocked

    def is_chamber_of_time_unlocked(self) -> bool:
        return self.chamber_of_time_unlocked

    def is_chamber_of_time_discovered(self) -> bool:
        return self.chamber_of_time_discovered

    def is_master_emblem_shown(self) -> bool:
        return self.master_emblem_shown

    def is_gate_keeper_dialog(self) -> bool:
        return self.gate_keeper_dialog

    def is_scratch_dialog(self) -> bool:
        return self.scratch_dialog

    def is_secret_shop_unlocked(self) -> bool:
        return self.secret_shop_unlocked

    def is_demon_guardian_dialog(self) -> bool:
        return self.demon_guardian_dialog

    def is_demon_freed(self) -> bool:
        return self.demon_freed

    def is_demon_key_1(self) -> bool:
        return self.demon_key_1

    def is_demon_key_2(self) -> bool:
        return self.demon_key_2

    def is_demon_key_3(self) -> bool:
        return self.demon_key_3

    def is_shop_keeper_dialog(self) -> bool:
        return self.shop_keeper_dialog

    def is_world_online_levels(self) -> bool:
        return self.world_online_levels

    def is_demon_discovered(self) -> bool:
        return self.demon_discovered

    def is_community_shop_unlocked(self) -> bool:
        return self.community_shop_unlocked

    def is_potbor_dialog(self) -> bool:
        return self.potbor_dialog

    def is_youtube_chest_unlocked(self) -> bool:
        return self.youtube_chest_unlocked

    def is_facebook_chest_unlocked(self) -> bool:
        return self.facebook_chest_unlocked

    def is_twitter_chest_unlocked(self) -> bool:
        return self.twitter_chest_unlocked

    # def is_firebird_gate_keeper(self) -> bool:
    #     return self.firebird_gate_keeper

    # def is_twitch_chest_unlocked(self) -> bool:
    #     return self.twitch_chest_unlocked

    # def is_discord_chest_unlocked(self) -> bool:
    #     return self.discord_chest_unlocked
