from functools import partial
from typing import Iterable, Mapping, Optional, Type, TypeVar

from iters.iters import iter

from gd.enum_extensions import Enum
from gd.models_constants import (
    COLOR_SEPARATOR,
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    DATABASE_SEPARATOR,
    EXTRA_STRING_SEPARATOR,
    FRIEND_REQUEST_SEPARATOR,
    FRIEND_REQUESTS_RESPONSE_FRIEND_REQUESTS_SEPARATOR,
    FRIEND_REQUESTS_RESPONSE_SEPARATOR,
    HEADER_SEPARATOR,
    HSV_SEPARATOR,
    LEADERBOARD_RESPONSE_USERS_SEPARATOR,
    LEADERBOARD_USER_SEPARATOR,
    LOGIN_SEPARATOR,
    MESSAGE_SEPARATOR,
    MESSAGES_RESPONSE_MESSAGES_SEPARATOR,
    MESSAGES_RESPONSE_SEPARATOR,
    OBJECTS_SEPARATOR,
    PAGE_SEPARATOR,
    PROFILE_SEPARATOR,
    RECORDING_SEPARATOR,
    RELATIONSHIP_USER_SEPARATOR,
    RELATIONSHIPS_RESPONSE_USERS_SEPARATOR,
    SEARCH_USER_SEPARATOR,
    SEARCH_USERS_RESPONSE_SEPARATOR,
    SEARCH_USERS_RESPONSE_USERS_SEPARATOR,
    SONG_SEPARATOR,
    TIME_SEPARATOR,
    TIME_SEPARATOR_SPACE,
    TIMELY_INFO_SEPARATOR,
)
from gd.typing import Parse


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
    return enum_type.from_value(parse(string))


def partial_parse_enum(parse: Parse[T], enum_type: Type[E]) -> Parse[E]:
    def actual_parse(string: str) -> E:
        return parse_enum(parse, enum_type, string)

    return actual_parse


def parse_get_or(parse: Parse[T], default: T, option: Optional[str]) -> T:
    if option is None:
        return default

    return parse(option)


def int_invert(string: str) -> bool:
    if not string:
        return True

    return not int(string)


DEFAULT_IGNORE_EMPTY = False


def split_iterable(
    separator: str, string: str, ignore_empty: bool = DEFAULT_IGNORE_EMPTY
) -> Iterable[str]:
    iterable = string.split(separator)

    if ignore_empty:
        return filter(None, iterable)

    return iterable


def split_string_mapping(separator: str, string: str) -> Mapping[str, str]:
    return {index: value for index, value in iter(string.split(separator)).pairs().unwrap()}


def split_mapping(separator: str, string: str) -> Mapping[int, str]:
    return {int(index): value for index, value in iter(string.split(separator)).pairs().unwrap()}


def string_mapping_to_iterable(mapping: Mapping[str, str]) -> Iterable[str]:
    return iter((index, value) for index, value in mapping.items()).flatten().unwrap()


def mapping_to_iterable(mapping: Mapping[int, str]) -> Iterable[str]:
    return iter((str(index), value) for index, value in mapping.items()).flatten().unwrap()


def concat_string_mapping(separator: str, mapping: Mapping[str, str]) -> str:
    return separator.join(string_mapping_to_iterable(mapping))


def concat_mapping(separator: str, mapping: Mapping[int, str]) -> str:
    return separator.join(mapping_to_iterable(mapping))


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

split_page = partial(split_iterable, PAGE_SEPARATOR)
concat_page = partial(concat_iterable, PAGE_SEPARATOR)

split_comment_banned = partial(split_iterable, COMMENT_BANNED_SEPARATOR)
concat_comment_banned = partial(concat_iterable, COMMENT_BANNED_SEPARATOR)

split_extra_string = partial(split_iterable, EXTRA_STRING_SEPARATOR)
concat_extra_string = partial(concat_iterable, EXTRA_STRING_SEPARATOR)

split_hsv = partial(split_iterable, HSV_SEPARATOR)
concat_hsv = partial(concat_iterable, HSV_SEPARATOR)

split_color = partial(split_iterable, COLOR_SEPARATOR)
concat_color = partial(concat_iterable, COLOR_SEPARATOR)

split_database = partial(split_iterable, DATABASE_SEPARATOR)
concat_database = partial(concat_iterable, DATABASE_SEPARATOR)

split_header = partial(split_string_mapping, HEADER_SEPARATOR)
concat_header = partial(concat_string_mapping, HEADER_SEPARATOR)

concat_recording = partial(concat_iterable, RECORDING_SEPARATOR)

split_objects = partial(split_iterable, OBJECTS_SEPARATOR)
concat_objects = partial(concat_iterable, OBJECTS_SEPARATOR)

split_time = partial(split_iterable, TIME_SEPARATOR)
concat_time = partial(concat_iterable, TIME_SEPARATOR_SPACE)

split_search_users_response = partial(split_iterable, SEARCH_USERS_RESPONSE_SEPARATOR)
concat_search_users_response = partial(concat_iterable, SEARCH_USERS_RESPONSE_SEPARATOR)

split_search_users_response_users = partial(
    split_iterable, SEARCH_USERS_RESPONSE_USERS_SEPARATOR, ignore_empty=True
)
concat_search_users_response_users = partial(concat_iterable, SEARCH_USERS_RESPONSE_USERS_SEPARATOR)

split_relationships_response_users = partial(
    split_iterable, RELATIONSHIPS_RESPONSE_USERS_SEPARATOR, ignore_empty=True
)
concat_relationships_response_users = partial(
    concat_iterable, RELATIONSHIPS_RESPONSE_USERS_SEPARATOR
)

split_leaderboard_response_users = partial(
    split_iterable, LEADERBOARD_RESPONSE_USERS_SEPARATOR, ignore_empty=True
)
concat_leaderboard_response_users = partial(concat_iterable, LEADERBOARD_RESPONSE_USERS_SEPARATOR)

split_messages_response = partial(split_iterable, MESSAGES_RESPONSE_SEPARATOR)
concat_messages_response = partial(concat_iterable, MESSAGES_RESPONSE_SEPARATOR)

split_messages_response_messages = partial(
    split_iterable, MESSAGES_RESPONSE_MESSAGES_SEPARATOR, ignore_empty=True
)
concat_messages_response_messages = partial(concat_iterable, MESSAGES_RESPONSE_MESSAGES_SEPARATOR)

split_friend_requests_response = partial(split_iterable, FRIEND_REQUESTS_RESPONSE_SEPARATOR)
concat_friend_requests_response = partial(concat_iterable, FRIEND_REQUESTS_RESPONSE_SEPARATOR)

split_friend_requests_response_friend_requests = partial(
    split_iterable, FRIEND_REQUESTS_RESPONSE_FRIEND_REQUESTS_SEPARATOR, ignore_empty=True
)
concat_friend_requests_response_friend_requests = partial(
    concat_iterable, FRIEND_REQUESTS_RESPONSE_FRIEND_REQUESTS_SEPARATOR
)
