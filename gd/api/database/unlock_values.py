from attrs import define
from typing_aliases import StringDict
from typing_extensions import Self

from gd.models_utils import bool_str, int_bool
from gd.robtop_view import StringRobTopView

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
X_CHEST_UNLOCKED = "ugv_24"
# FIREBIRD_GATE_KEEPER = "ugv_25"
# TWITCH_CHEST_UNLOCKED = "ugv_26"
# DISCORD_CHEST_UNLOCKED = "ugv_27"


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
DEFAULT_X_CHEST_UNLOCKED = False
# DEFAULT_FIREBIRD_GATE_KEEPER = False
# DEFAULT_TWITCH_CHEST_UNLOCKED = False
# DEFAULT_DISCORD_CHEST_UNLOCKED = False


@define()
class UnlockValues:
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
    x_chest_unlocked: bool = DEFAULT_X_CHEST_UNLOCKED
    # firebird_gate_keeper: bool = DEFAULT_FIREBIRD_GATE_KEEPER
    # twitch_chest_unlocked: bool = DEFAULT_TWITCH_CHEST_UNLOCKED
    # discord_chest_unlocked: bool = DEFAULT_DISCORD_CHEST_UNLOCKED

    @classmethod
    def from_robtop_data(cls, view: StringRobTopView[str]) -> Self:
        the_challenge_unlocked = (
            view.get_option(THE_CHALLENGE_UNLOCKED)
            .map(int_bool)
            .unwrap_or(DEFAULT_THE_CHALLENGE_UNLOCKED)
        )
        gubflub_hint_1 = (
            view.get_option(GUBFLUB_HINT_1).map(int_bool).unwrap_or(DEFAULT_GUBFLUB_HINT_1)
        )
        gubflub_hint_2 = (
            view.get_option(GUBFLUB_HINT_2).map(int_bool).unwrap_or(DEFAULT_GUBFLUB_HINT_2)
        )
        the_challenge_completed = (
            view.get_option(THE_CHALLENGE_COMPLETED)
            .map(int_bool)
            .unwrap_or(DEFAULT_THE_CHALLENGE_COMPLETED)
        )
        treasure_room_unlocked = (
            view.get_option(TREASURE_ROOM_UNLOCKED)
            .map(int_bool)
            .unwrap_or(DEFAULT_TREASURE_ROOM_UNLOCKED)
        )
        chamber_of_time_unlocked = (
            view.get_option(CHAMBER_OF_TIME_UNLOCKED)
            .map(int_bool)
            .unwrap_or(DEFAULT_CHAMBER_OF_TIME_UNLOCKED)
        )
        chamber_of_time_discovered = (
            view.get_option(CHAMBER_OF_TIME_DISCOVERED)
            .map(int_bool)
            .unwrap_or(DEFAULT_CHAMBER_OF_TIME_DISCOVERED)
        )
        master_emblem_shown = (
            view.get_option(MASTER_EMBLEM_SHOWN)
            .map(int_bool)
            .unwrap_or(DEFAULT_MASTER_EMBLEM_SHOWN)
        )
        gate_keeper_dialog = (
            view.get_option(GATE_KEEPER_DIALOG).map(int_bool).unwrap_or(DEFAULT_GATE_KEEPER_DIALOG)
        )
        scratch_dialog = (
            view.get_option(SCRATCH_DIALOG).map(int_bool).unwrap_or(DEFAULT_SCRATCH_DIALOG)
        )
        secret_shop_unlocked = (
            view.get_option(SECRET_SHOP_UNLOCKED)
            .map(int_bool)
            .unwrap_or(DEFAULT_SECRET_SHOP_UNLOCKED)
        )
        demon_guardian_dialog = (
            view.get_option(DEMON_GUARDIAN_DIALOG)
            .map(int_bool)
            .unwrap_or(DEFAULT_DEMON_GUARDIAN_DIALOG)
        )
        demon_freed = view.get_option(DEMON_FREED).map(int_bool).unwrap_or(DEFAULT_DEMON_FREED)
        demon_key_1 = view.get_option(DEMON_KEY_1).map(int_bool).unwrap_or(DEFAULT_DEMON_KEY_1)
        demon_key_2 = view.get_option(DEMON_KEY_2).map(int_bool).unwrap_or(DEFAULT_DEMON_KEY_2)
        demon_key_3 = view.get_option(DEMON_KEY_3).map(int_bool).unwrap_or(DEFAULT_DEMON_KEY_3)
        shop_keeper_dialog = (
            view.get_option(SHOP_KEEPER_DIALOG).map(int_bool).unwrap_or(DEFAULT_SHOP_KEEPER_DIALOG)
        )
        world_online_levels = (
            view.get_option(WORLD_ONLINE_LEVELS)
            .map(int_bool)
            .unwrap_or(DEFAULT_WORLD_ONLINE_LEVELS)
        )
        demon_discovered = (
            view.get_option(DEMON_DISCOVERED).map(int_bool).unwrap_or(DEFAULT_DEMON_DISCOVERED)
        )
        community_shop_unlocked = (
            view.get_option(COMMUNITY_SHOP_UNLOCKED)
            .map(int_bool)
            .unwrap_or(DEFAULT_COMMUNITY_SHOP_UNLOCKED)
        )
        potbor_dialog = (
            view.get_option(POTBOR_DIALOG).map(int_bool).unwrap_or(DEFAULT_POTBOR_DIALOG)
        )
        youtube_chest_unlocked = (
            view.get_option(YOUTUBE_CHEST_UNLOCKED)
            .map(int_bool)
            .unwrap_or(DEFAULT_YOUTUBE_CHEST_UNLOCKED)
        )
        facebook_chest_unlocked = (
            view.get_option(FACEBOOK_CHEST_UNLOCKED)
            .map(int_bool)
            .unwrap_or(DEFAULT_FACEBOOK_CHEST_UNLOCKED)
        )
        x_chest_unlocked = (
            view.get_option(X_CHEST_UNLOCKED).map(int_bool).unwrap_or(DEFAULT_X_CHEST_UNLOCKED)
        )
        # firebird_gate_keeper = (
        #     view.get_option(FIREBIRD_GATE_KEEPER)
        #     .map(int_bool)
        #     .unwrap_or(DEFAULT_FIREBIRD_GATE_KEEPER)
        # )
        # twitch_chest_unlocked = (
        #     view.get_option(TWITCH_CHEST_UNLOCKED)
        #     .map(int_bool)
        #     .unwrap_or(DEFAULT_TWITCH_CHEST_UNLOCKED)
        # )
        # discord_chest_unlocked = (
        #     view.get_option(DISCORD_CHEST_UNLOCKED)
        #     .map(int_bool)
        #     .unwrap_or(DEFAULT_DISCORD_CHEST_UNLOCKED)
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
            x_chest_unlocked=x_chest_unlocked,
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

        x_chest_unlocked = self.is_x_chest_unlocked()

        if x_chest_unlocked:
            data[X_CHEST_UNLOCKED] = bool_str(x_chest_unlocked)

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

    def is_x_chest_unlocked(self) -> bool:
        return self.x_chest_unlocked

    # def is_firebird_gate_keeper(self) -> bool:
    #     return self.firebird_gate_keeper

    # def is_twitch_chest_unlocked(self) -> bool:
    #     return self.twitch_chest_unlocked

    # def is_discord_chest_unlocked(self) -> bool:
    #     return self.discord_chest_unlocked
