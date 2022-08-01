from functools import partial
from typing import Iterable, Mapping

from iters.iters import iter

from gd.models_constants import (
    COLOR_SEPARATOR,
    COMMENT_BANNED_SEPARATOR,
    CREATOR_SEPARATOR,
    DATABASE_SEPARATOR,
    EXTRA_STRING_SEPARATOR,
    HEADER_SEPARATOR,
    HSV_SEPARATOR,
    LOGIN_SEPARATOR,
    OBJECTS_SEPARATOR,
    PAGE_SEPARATOR,
    RECORDING_SEPARATOR,
    SONG_SEPARATOR,
    TIME_SEPARATOR,
    TIME_SEPARATOR_SPACE,
)

FALSE = str(0)
TRUE = str(1)
TRUE_TOO = str(2)


def float_str(value: float) -> str:
    whole = int(value)

    return str(whole) if whole == value else str(value)


def bool_str(value: bool, true: str = TRUE, false: str = FALSE) -> str:
    return true if value else false


def int_bool(string: str) -> bool:
    if not string:
        return False

    return bool(int(string))


def split_iterable(separator: str, string: str) -> Iterable[str]:
    return string.split(separator)


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
