from re import compile
from typing import Match

__all__ = ("camel_to_snake", "snake_to_camel")

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
