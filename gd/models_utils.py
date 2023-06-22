from enum import Enum
from typing import Iterable, Mapping, Optional, Type, TypeVar

from funcs.application import partial
from iters.iters import iter
from typing_aliases import NormalError, Nullary, Pair, Parse

from gd.models_constants import (
    ARTIST_SEPARATOR,
    ARTISTS_RESPONSE_ARTISTS_SEPARATOR,
    ARTISTS_RESPONSE_SEPARATOR,
    CAPACITY_SEPARATOR,
    CHEST_SEPARATOR,
    CHESTS_INNER_SEPARATOR,
    CHESTS_RESPONSE_SEPARATOR,
    COLOR_CHANNEL_SEPARATOR,
    COLOR_CHANNELS_SEPARATOR,
    COLOR_SEPARATOR,
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    FRIEND_REQUEST_SEPARATOR,
    FRIEND_REQUESTS_RESPONSE_FRIEND_REQUESTS_SEPARATOR,
    FRIEND_REQUESTS_RESPONSE_SEPARATOR,
    GAUNTLET_SEPARATOR,
    GAUNTLETS_RESPONSE_GAUNTLETS_SEPARATOR,
    GAUNTLETS_RESPONSE_SEPARATOR,
    GROUPS_SEPARATOR,
    GUIDELINES_SEPARATOR,
    HEADER_SEPARATOR,
    HSV_SEPARATOR,
    LEADERBOARD_RESPONSE_USERS_SEPARATOR,
    LEADERBOARD_USER_SEPARATOR,
    LEVEL_COMMENT_INNER_SEPARATOR,
    LEVEL_COMMENT_SEPARATOR,
    LEVEL_COMMENT_USER_SEPARATOR,
    LEVEL_COMMENTS_RESPONSE_COMMENTS_SEPARATOR,
    LEVEL_COMMENTS_RESPONSE_SEPARATOR,
    LEVEL_IDS_SEPARATOR,
    LEVEL_LEADERBOARD_RESPONSE_USERS_SEPARATOR,
    LEVEL_LEADERBOARD_USER_SEPARATOR,
    LEVEL_RESPONSE_SEPARATOR,
    LEVEL_SEPARATOR,
    LIKE_SEPARATOR,
    LOGIN_SEPARATOR,
    MAP_PACK_SEPARATOR,
    MAP_PACKS_RESPONSE_MAP_PACKS_SEPARATOR,
    MAP_PACKS_RESPONSE_SEPARATOR,
    MESSAGE_SEPARATOR,
    MESSAGES_RESPONSE_MESSAGES_SEPARATOR,
    MESSAGES_RESPONSE_SEPARATOR,
    NAME_SEPARATOR,
    OBJECT_SEPARATOR,
    OBJECTS_SEPARATOR,
    PAGE_SEPARATOR,
    PROFILE_SEPARATOR,
    PROGRESS_SEPARATOR,
    QUEST_SEPARATOR,
    QUESTS_INNER_SEPARATOR,
    QUESTS_RESPONSE_SEPARATOR,
    RECORDING_ITEM_SEPARATOR,
    RELATIONSHIP_USER_SEPARATOR,
    RELATIONSHIPS_RESPONSE_USERS_SEPARATOR,
    SAVE_SEPARATOR,
    SEARCH_LEVELS_RESPONSE_CREATORS_SEPARATOR,
    SEARCH_LEVELS_RESPONSE_LEVELS_SEPARATOR,
    SEARCH_LEVELS_RESPONSE_SEPARATOR,
    SEARCH_LEVELS_RESPONSE_SONGS_SEPARATOR,
    SEARCH_USER_SEPARATOR,
    SEARCH_USERS_RESPONSE_SEPARATOR,
    SEARCH_USERS_RESPONSE_USERS_SEPARATOR,
    SONG_SEPARATOR,
    TIME_SEPARATOR,
    TIME_SEPARATOR_SPACE,
    TIMELY_INFO_SEPARATOR,
    USER_COMMENT_SEPARATOR,
    USER_COMMENTS_RESPONSE_COMMENTS_SEPARATOR,
    USER_COMMENTS_RESPONSE_SEPARATOR,
)


def round_float(string: str) -> int:
    return round(float(string))


def bool_str(value: bool) -> str:
    return str(int(value))


def float_str(value: float) -> str:
    whole = int(value)

    return str(whole) if whole == value else str(value)


def int_bool(string: str) -> bool:
    if not string:
        return False

    return bool(int(string))


E = TypeVar("E", bound=Enum)
T = TypeVar("T")


def parse_enum(parse: Parse[T], enum_type: Type[E], string: str) -> E:
    return enum_type(parse(string))


def partial_parse_enum(parse: Parse[T], enum_type: Type[E]) -> Parse[E]:
    def actual_parse(string: str) -> E:
        return parse_enum(parse, enum_type, string)

    return actual_parse


DEFAULT_IGNORE_ERRORS = False


def parse_get_or(
    parse: Parse[T], default: T, option: Optional[str], ignore_errors: bool = DEFAULT_IGNORE_ERRORS
) -> T:
    if option is None:
        return default

    try:
        return parse(option)

    except NormalError:
        if ignore_errors:
            return default

        raise


def parse_get_or_else(
    parse: Parse[T],
    default: Nullary[T],
    option: Optional[str],
    ignore_errors: bool = DEFAULT_IGNORE_ERRORS,
) -> T:
    if option is None:
        return default()

    try:
        return parse(option)

    except NormalError:
        if ignore_errors:
            return default()

        raise


def split_iterable(separator: str, string: str) -> Iterable[str]:
    if not string:
        return []

    return string.split(separator)


def split_string_mapping(separator: str, string: str) -> Mapping[str, str]:
    if not string:
        return {}

    return {index: value for index, value in iter(string.split(separator)).pairs().unwrap()}


def split_mapping(separator: str, string: str) -> Mapping[int, str]:
    if not string:
        return {}

    return {int(index): value for index, value in iter(string.split(separator)).pairs().unwrap()}


def split_float_mapping(separator: str, string: str) -> Mapping[float, float]:
    if not string:
        return {}

    return {
        float(key): float(value)
        for key, value in iter(string.split(separator)).filter(None).pairs().unwrap()
    }


def string_mapping_to_iterable(mapping: Mapping[str, str]) -> Iterable[str]:
    return iter(mapping.items()).flatten().unwrap()


def str_left(left: int, right: str) -> Pair[str]:
    return (str(left), right)


def mapping_to_iterable(mapping: Mapping[int, str]) -> Iterable[str]:
    return iter((str(index), value) for index, value in mapping.items()).flatten().unwrap()


def float_mapping_to_iterable(mapping: Mapping[float, float]) -> Iterable[str]:
    return iter((str(key), str(value)) for key, value in mapping.items()).flatten().unwrap()


def concat_string_mapping(separator: str, mapping: Mapping[str, str]) -> str:
    return separator.join(string_mapping_to_iterable(mapping))


def concat_mapping(separator: str, mapping: Mapping[int, str]) -> str:
    return separator.join(mapping_to_iterable(mapping))


def concat_float_mapping(separator: str, mapping: Mapping[float, float]) -> str:
    return separator.join(float_mapping_to_iterable(mapping))


def concat_iterable(separator: str, iterable: Iterable[str]) -> str:
    return separator.join(iterable)


split_song = partial(split_mapping, SONG_SEPARATOR)
concat_song = partial(concat_mapping, SONG_SEPARATOR)

split_login = partial(split_iterable, LOGIN_SEPARATOR)
concat_login = partial(concat_iterable, LOGIN_SEPARATOR)

split_creator = partial(split_iterable, CREATOR_SEPARATOR)
concat_creator = partial(concat_iterable, CREATOR_SEPARATOR)

split_search_user = partial(split_mapping, SEARCH_USER_SEPARATOR)
concat_search_user = partial(concat_mapping, SEARCH_USER_SEPARATOR)

split_profile = partial(split_mapping, PROFILE_SEPARATOR)
concat_profile = partial(concat_mapping, PROFILE_SEPARATOR)

split_relationship_user = partial(split_mapping, RELATIONSHIP_USER_SEPARATOR)
concat_relationship_user = partial(concat_mapping, RELATIONSHIP_USER_SEPARATOR)

split_leaderboard_user = partial(split_mapping, LEADERBOARD_USER_SEPARATOR)
concat_leaderboard_user = partial(concat_mapping, LEADERBOARD_USER_SEPARATOR)

split_timely_info = partial(split_iterable, TIMELY_INFO_SEPARATOR)
concat_timely_info = partial(concat_iterable, TIMELY_INFO_SEPARATOR)

split_message = partial(split_mapping, MESSAGE_SEPARATOR)
concat_message = partial(concat_mapping, MESSAGE_SEPARATOR)

split_friend_request = partial(split_mapping, FRIEND_REQUEST_SEPARATOR)
concat_friend_request = partial(concat_mapping, FRIEND_REQUEST_SEPARATOR)

split_level = partial(split_mapping, LEVEL_SEPARATOR)
concat_level = partial(concat_mapping, LEVEL_SEPARATOR)

split_level_comment_inner = partial(split_mapping, LEVEL_COMMENT_INNER_SEPARATOR)
concat_level_comment_inner = partial(concat_mapping, LEVEL_COMMENT_INNER_SEPARATOR)

split_level_comment_user = partial(split_mapping, LEVEL_COMMENT_USER_SEPARATOR)
concat_level_comment_user = partial(concat_mapping, LEVEL_COMMENT_USER_SEPARATOR)

split_level_leaderboard_user = partial(split_mapping, LEVEL_LEADERBOARD_USER_SEPARATOR)
concat_level_leaderboard_user = partial(concat_mapping, LEVEL_LEADERBOARD_USER_SEPARATOR)

split_artist = partial(split_mapping, ARTIST_SEPARATOR)
concat_artist = partial(concat_mapping, ARTIST_SEPARATOR)

split_level_comment = partial(split_iterable, LEVEL_COMMENT_SEPARATOR)
concat_level_comment = partial(concat_iterable, LEVEL_COMMENT_SEPARATOR)

split_user_comment = partial(split_mapping, USER_COMMENT_SEPARATOR)
concat_user_comment = partial(concat_mapping, USER_COMMENT_SEPARATOR)

split_gauntlet = partial(split_mapping, GAUNTLET_SEPARATOR)
concat_gauntlet = partial(concat_mapping, GAUNTLET_SEPARATOR)

split_map_pack = partial(split_mapping, MAP_PACK_SEPARATOR)
concat_map_pack = partial(concat_mapping, MAP_PACK_SEPARATOR)

split_chest = partial(split_iterable, CHEST_SEPARATOR)
concat_chest = partial(concat_iterable, CHEST_SEPARATOR)

split_quest = partial(split_iterable, QUEST_SEPARATOR)
concat_quest = partial(concat_iterable, QUEST_SEPARATOR)

split_chests_inner = partial(split_iterable, CHESTS_INNER_SEPARATOR)
concat_chests_inner = partial(concat_iterable, CHESTS_INNER_SEPARATOR)

split_quests_inner = partial(split_iterable, QUESTS_INNER_SEPARATOR)
concat_quests_inner = partial(concat_iterable, QUESTS_INNER_SEPARATOR)

split_level_ids = partial(split_iterable, LEVEL_IDS_SEPARATOR)
concat_level_ids = partial(concat_iterable, LEVEL_IDS_SEPARATOR)

split_name = partial(split_iterable, NAME_SEPARATOR)
concat_name = partial(concat_iterable, NAME_SEPARATOR)

split_like = partial(split_iterable, LIKE_SEPARATOR)
concat_like = partial(concat_iterable, LIKE_SEPARATOR)

split_page = partial(split_iterable, PAGE_SEPARATOR)
concat_page = partial(concat_iterable, PAGE_SEPARATOR)

split_comment_banned = partial(split_iterable, COMMENT_BANNED_SEPARATOR)
concat_comment_banned = partial(concat_iterable, COMMENT_BANNED_SEPARATOR)

concat_recording_item = partial(concat_iterable, RECORDING_ITEM_SEPARATOR)

split_hsv = partial(split_iterable, HSV_SEPARATOR)
concat_hsv = partial(concat_iterable, HSV_SEPARATOR)

split_color = partial(split_iterable, COLOR_SEPARATOR)
concat_color = partial(concat_iterable, COLOR_SEPARATOR)

split_header = partial(split_string_mapping, HEADER_SEPARATOR)
concat_header = partial(concat_string_mapping, HEADER_SEPARATOR)

split_color_channel = partial(split_mapping, COLOR_CHANNEL_SEPARATOR)
concat_color_channel = partial(concat_mapping, COLOR_CHANNEL_SEPARATOR)

split_color_channels = partial(split_iterable, COLOR_CHANNELS_SEPARATOR)
concat_color_channels = partial(concat_iterable, COLOR_CHANNELS_SEPARATOR)

split_objects = partial(split_iterable, OBJECTS_SEPARATOR)
concat_objects = partial(concat_iterable, OBJECTS_SEPARATOR)

split_object = partial(split_mapping, OBJECT_SEPARATOR)
concat_object = partial(concat_mapping, OBJECT_SEPARATOR)

split_any_object = partial(split_string_mapping, OBJECT_SEPARATOR)
concat_any_object = partial(concat_string_mapping, OBJECT_SEPARATOR)

split_groups = partial(split_iterable, GROUPS_SEPARATOR)
concat_groups = partial(concat_iterable, GROUPS_SEPARATOR)

split_guidelines = partial(split_float_mapping, GUIDELINES_SEPARATOR)
concat_guidelines = partial(concat_float_mapping, GUIDELINES_SEPARATOR)

split_save = partial(split_iterable, SAVE_SEPARATOR)
concat_save = partial(concat_iterable, SAVE_SEPARATOR)

split_time = partial(split_iterable, TIME_SEPARATOR)
concat_time = partial(concat_iterable, TIME_SEPARATOR_SPACE)

split_artists_response = partial(split_iterable, ARTISTS_RESPONSE_SEPARATOR)
concat_artists_response = partial(concat_iterable, ARTISTS_RESPONSE_SEPARATOR)

split_artists_response_artists = partial(split_iterable, ARTISTS_RESPONSE_ARTISTS_SEPARATOR)
concat_artists_response_artists = partial(concat_iterable, ARTISTS_RESPONSE_ARTISTS_SEPARATOR)

split_search_users_response = partial(split_iterable, SEARCH_USERS_RESPONSE_SEPARATOR)
concat_search_users_response = partial(concat_iterable, SEARCH_USERS_RESPONSE_SEPARATOR)

split_search_users_response_users = partial(split_iterable, SEARCH_USERS_RESPONSE_USERS_SEPARATOR)
concat_search_users_response_users = partial(concat_iterable, SEARCH_USERS_RESPONSE_USERS_SEPARATOR)

split_relationships_response_users = partial(split_iterable, RELATIONSHIPS_RESPONSE_USERS_SEPARATOR)
concat_relationships_response_users = partial(
    concat_iterable, RELATIONSHIPS_RESPONSE_USERS_SEPARATOR
)

split_leaderboard_response_users = partial(split_iterable, LEADERBOARD_RESPONSE_USERS_SEPARATOR)
concat_leaderboard_response_users = partial(concat_iterable, LEADERBOARD_RESPONSE_USERS_SEPARATOR)

split_messages_response = partial(split_iterable, MESSAGES_RESPONSE_SEPARATOR)
concat_messages_response = partial(concat_iterable, MESSAGES_RESPONSE_SEPARATOR)

split_messages_response_messages = partial(split_iterable, MESSAGES_RESPONSE_MESSAGES_SEPARATOR)
concat_messages_response_messages = partial(concat_iterable, MESSAGES_RESPONSE_MESSAGES_SEPARATOR)

split_friend_requests_response = partial(split_iterable, FRIEND_REQUESTS_RESPONSE_SEPARATOR)
concat_friend_requests_response = partial(concat_iterable, FRIEND_REQUESTS_RESPONSE_SEPARATOR)

split_friend_requests_response_friend_requests = partial(
    split_iterable, FRIEND_REQUESTS_RESPONSE_FRIEND_REQUESTS_SEPARATOR
)
concat_friend_requests_response_friend_requests = partial(
    concat_iterable, FRIEND_REQUESTS_RESPONSE_FRIEND_REQUESTS_SEPARATOR
)

split_level_response = partial(split_iterable, LEVEL_RESPONSE_SEPARATOR)
concat_level_response = partial(concat_iterable, LEVEL_RESPONSE_SEPARATOR)

split_search_levels_response = partial(split_iterable, SEARCH_LEVELS_RESPONSE_SEPARATOR)
concat_search_levels_response = partial(concat_iterable, SEARCH_LEVELS_RESPONSE_SEPARATOR)

split_search_levels_response_levels = partial(
    split_iterable, SEARCH_LEVELS_RESPONSE_LEVELS_SEPARATOR
)
concat_search_levels_response_levels = partial(
    concat_iterable, SEARCH_LEVELS_RESPONSE_LEVELS_SEPARATOR
)

split_search_levels_response_creators = partial(
    split_iterable, SEARCH_LEVELS_RESPONSE_CREATORS_SEPARATOR
)
concat_search_levels_response_creators = partial(
    concat_iterable, SEARCH_LEVELS_RESPONSE_CREATORS_SEPARATOR
)

split_search_levels_response_songs = partial(split_iterable, SEARCH_LEVELS_RESPONSE_SONGS_SEPARATOR)
concat_search_levels_response_songs = partial(
    concat_iterable, SEARCH_LEVELS_RESPONSE_SONGS_SEPARATOR
)

split_user_comments_response = partial(split_iterable, USER_COMMENTS_RESPONSE_SEPARATOR)
concat_user_comments_response = partial(concat_iterable, USER_COMMENTS_RESPONSE_SEPARATOR)

split_user_comments_response_comments = partial(
    split_iterable, USER_COMMENTS_RESPONSE_COMMENTS_SEPARATOR
)
concat_user_comments_response_comments = partial(
    concat_iterable, USER_COMMENTS_RESPONSE_COMMENTS_SEPARATOR
)

split_level_comments_response = partial(split_iterable, LEVEL_COMMENTS_RESPONSE_SEPARATOR)
concat_level_comments_response = partial(concat_iterable, LEVEL_COMMENTS_RESPONSE_SEPARATOR)

split_level_comments_response_comments = partial(
    split_iterable, LEVEL_COMMENTS_RESPONSE_COMMENTS_SEPARATOR
)
concat_level_comments_response_comments = partial(
    concat_iterable, LEVEL_COMMENTS_RESPONSE_COMMENTS_SEPARATOR
)

split_level_leaderboard_response_users = partial(
    split_iterable, LEVEL_LEADERBOARD_RESPONSE_USERS_SEPARATOR
)
concat_level_leaderboard_response_users = partial(
    concat_iterable, LEVEL_LEADERBOARD_RESPONSE_USERS_SEPARATOR
)

split_progress = partial(split_iterable, PROGRESS_SEPARATOR)
concat_progress = partial(concat_iterable, PROGRESS_SEPARATOR)

split_chests_response = partial(split_iterable, CHESTS_RESPONSE_SEPARATOR)
concat_chests_response = partial(concat_iterable, CHESTS_RESPONSE_SEPARATOR)

split_quests_response = partial(split_iterable, QUESTS_RESPONSE_SEPARATOR)
concat_quests_response = partial(concat_iterable, QUESTS_RESPONSE_SEPARATOR)

split_map_packs_response = partial(split_iterable, MAP_PACKS_RESPONSE_SEPARATOR)
concat_map_packs_response = partial(concat_iterable, MAP_PACKS_RESPONSE_SEPARATOR)

split_map_packs_response_map_packs = partial(split_iterable, MAP_PACKS_RESPONSE_MAP_PACKS_SEPARATOR)
concat_map_packs_response_map_packs = partial(
    concat_iterable, MAP_PACKS_RESPONSE_MAP_PACKS_SEPARATOR
)

split_gauntlets_response = partial(split_iterable, GAUNTLETS_RESPONSE_SEPARATOR)
concat_gauntlets_response = partial(concat_iterable, GAUNTLETS_RESPONSE_SEPARATOR)

split_gauntlets_response_gauntlets = partial(split_iterable, GAUNTLETS_RESPONSE_GAUNTLETS_SEPARATOR)
concat_gauntlets_response_gauntlets = partial(
    concat_iterable, GAUNTLETS_RESPONSE_GAUNTLETS_SEPARATOR
)

split_capacity = partial(split_iterable, CAPACITY_SEPARATOR)
concat_capacity = partial(concat_iterable, CAPACITY_SEPARATOR)
