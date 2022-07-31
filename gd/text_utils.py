from re import compile
from typing import Match

__all__ = ("camel_to_snake", "snake_to_camel", "to_ordinal")

UPPER = r"[A-Z]"
LOWER = r"[a-z]"

CAMEL_TO_SNAKE_PATTERN = rf"(?!^)({UPPER}+)"
SNAKE_TO_CAMEL_PATTERN = rf"(?!^)_({LOWER})"

CAMEL_TO_SNAKE = compile(CAMEL_TO_SNAKE_PATTERN)
SNAKE_TO_CAMEL = compile(SNAKE_TO_CAMEL_PATTERN)


def upper_case_first_group(match: Match[str]) -> str:
    return match.group(1).upper()


PREFIX = "_"


def lower_case_first_group(match: Match[str], prefix: str = PREFIX) -> str:
    return prefix + match.group(1).lower()


def camel_to_snake(string: str) -> str:
    """Converts `string` from `camelCase` to `snake_case`.

    Arguments:
        string: The `camelCase` string to convert to `snake_case`.

    Returns:
        The resulting `snake_case` string.
    """
    return CAMEL_TO_SNAKE.sub(lower_case_first_group, string).lower()


def snake_to_camel(string: str) -> str:
    """Converts `string` from `snake_case` to `camelCase`.

    Arguments:
        string: The `snake_case` string to convert to `camelCase`.

    Returns:
        The resulting `camelCase` string.
    """
    return SNAKE_TO_CAMEL.sub(upper_case_first_group, string)


ORDINAL_SUFFIXES = ("th", "st", "nd", "rd", "th")  # 0th, 1st, 2nd, 3rd, 4th, ...
ORDINAL_LAST_INDEX = len(ORDINAL_SUFFIXES) - 1
ORDINAL_LAST = ORDINAL_SUFFIXES[ORDINAL_LAST_INDEX]


def to_ordinal(value: int) -> str:
    """Converts the `value` to an ordinal, for example:

    | `number` | `ordinal` |
    |----------|-----------|
    | ``0``    | ``0th``   |
    | ``1``    | ``1st``   |
    | ``13``   | ``13th``  |
    | ``42``   | ``42nd``  |

    Arguments:
        value: The value to convert to an ordinal.

    Returns:
        An ordinal string representing the value.
    """
    suffix = ORDINAL_SUFFIXES[value % 10 % ORDINAL_LAST_INDEX]

    if 10 < value % 100 < 14:
        suffix = ORDINAL_LAST

    return str(value) + suffix
