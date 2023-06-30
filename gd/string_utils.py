from re import compile
from typing import Iterable, Match

from iters.utils import unary_tuple

from gd.constants import BACKSLASH, EMPTY, SPACE
from gd.string_constants import BRACES, COMMA, MAPS, PIPE, STAR, TICK, UNDER, WRAP, ZERO_PAD

__all__ = (
    # concatenation
    "concat_empty",
    "concat_space",
    "concat_comma",
    "concat_pipe",
    "concat_under",
    # wrapping
    "wrap",
    "tick",
    "maps",
    # aliases
    "is_upper",
    "is_lower",
    "case_fold",
    # functions
    "zero_pad",
    "clear_whitespace",
    "remove_escapes",
    # passwords
    "password_str",
    "password_repr",
    # case convertions
    "create_title",
    "camel_to_snake",
    "snake_to_camel",
    "snake_to_camel_with_abbreviations",
)

concat_empty = EMPTY.join
concat_space = SPACE.join
concat_comma = COMMA.join
concat_pipe = PIPE.join
concat_under = UNDER.join

wrap = WRAP.format
tick = TICK.format
maps = MAPS.format

create_translation = str.maketrans
dict_from_keys = dict.fromkeys

remove_braces = create_translation(dict_from_keys(BRACES, EMPTY))

starts_with = str.startswith
ends_with = str.endswith

is_digit = str.isdigit
is_upper = str.isupper
is_lower = str.islower

case_fold = str.casefold


try:
    remove_prefix = str.removeprefix  # type: ignore
    remove_suffix = str.removesuffix  # type: ignore

except AttributeError:

    def remove_prefix(self: str, prefix: str) -> str:
        if starts_with(self, prefix):
            return self[len(prefix) :]

        return self

    def remove_suffix(self: str, suffix: str) -> str:
        if ends_with(self, suffix):
            return self[: -len(suffix)]

        return self


def zero_pad(align: int, value: int) -> str:
    return ZERO_PAD.format(value=value, align=align)


def clear_whitespace(string: str) -> str:
    return concat_empty(string.split())


def remove_escapes(string: str) -> str:
    return string.replace(BACKSLASH, EMPTY)


def password_str(password: str) -> str:
    return STAR * len(password)


def password_repr(password: str) -> str:
    return repr(password_str(password))


def create_title(name: str) -> str:
    if is_upper(name) or is_lower(name):
        return name.replace(UNDER, SPACE).title()

    return name


UPPER = r"[0-9A-Z]"
LOWER = r"[0-9a-z]"

CAMEL_TO_SNAKE_PATTERN = rf"(?!^)({UPPER}+)"
SNAKE_TO_CAMEL_PATTERN = rf"(?!^)_({LOWER})"

CAMEL_TO_SNAKE = compile(CAMEL_TO_SNAKE_PATTERN)
SNAKE_TO_CAMEL = compile(SNAKE_TO_CAMEL_PATTERN)


def upper_case_first_group(match: Match[str]) -> str:
    return match.group(1).upper()


def lower_case_first_group(match: Match[str], prefix: str = UNDER) -> str:
    return prefix + match.group(1).lower()


def camel_to_snake(string: str) -> str:
    return CAMEL_TO_SNAKE.sub(lower_case_first_group, string)


def snake_to_camel(string: str) -> str:
    return SNAKE_TO_CAMEL.sub(upper_case_first_group, string)


ABBREVIATIONS = unary_tuple("ID")


def snake_to_camel_with_abbreviations(
    string: str, abbreviations: Iterable[str] = ABBREVIATIONS
) -> str:
    string = snake_to_camel(string)

    for abbreviation in abbreviations:
        string = string.replace(abbreviation.title(), abbreviation)

    return string
