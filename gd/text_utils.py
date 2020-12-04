import re

from gd.typing import AnyStr, Dict, Match, Optional, TypeVar

__all__ = (
    "make_repr",
    "object_count",
    "is_level_probably_decoded",
    "is_save_probably_decoded",
    "concat",
    "camel_to_snake",
    "snake_to_camel",
    "is_snake",
    "is_camel",
    "to_ordinal",
)

CAMEL_TO_SNAKE = re.compile(r"(?!^)([A-Z])")
SNAKE_TO_CAMEL = re.compile(r"(?!^)_([a-z])")
TEST_CAMEL = re.compile(r"(?:_*)[a-z]+(?:[A-Z][a-z0-9]+)*(?:_*)")
TEST_SNAKE = re.compile(r"(?:_*)(?:[a-z0-9]+_*)+(?:_*)")

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

concat = "".join

_BYTE_LEVEL_DELIM = b";"

_LEVEL_DELIM = ";"

_HEADER_DELIM = ","


def is_level_probably_decoded(string: str) -> bool:
    """Check if string *might* be decoded level data.
    This check simply searches for ``;`` or ``,`` in the ``string``.

    Parameters
    ----------
    string: :class:`str`
        String to check.

    Returns
    -------
    :class:`bool`
        Whether the ``string`` *might* be decoded level data.
    """
    return _LEVEL_DELIM in string or _HEADER_DELIM in string


_XML_OPEN_TAG = "<"
_XML_CLOSE_TAG = ">"


def is_save_probably_decoded(string: str) -> bool:
    """Check if string *might* be XML data.
    This check simply searches for ``<`` **and** ``>`` in the ``string``.

    Parameters
    ----------
    string: :class:`str`
        String to check.

    Returns
    -------
    :class:`bool`
        Whether the ``string`` *might* be XML data.
    """
    return _XML_OPEN_TAG in string and _XML_CLOSE_TAG in string


def make_repr(some_object: T, info: Optional[Dict[K, V]] = None, delim: str = " ",) -> str:
    """Create a nice representation of an object.

    Parameters
    ----------
    some_object: ``T``
        Object to create ``repr()`` of.

    info: Optional[Dict[``K``, ``V``]]
        Additional information to add. If ``None`` or not given, no info is attached.

    delim: :class:`str`
        Delimiter to split parts of ``info`` with.

    Returns
    -------
    :class:`str`
        ``repr()`` of ``some_object``.
    """
    name = some_object.__class__.__name__

    if not info:
        return f"<{name}>"

    formatted_info = delim.join(f"{key}={value}" for key, value in info.items())

    return f"<{name} {formatted_info}>"


def upper_first_group(match: Match) -> str:
    return match.group(1).upper()


def lower_first_group(match: Match) -> str:
    return "_" + match.group(1).lower()


def camel_to_snake(string: str) -> str:
    """Convert ``string`` from ``camelCase`` to ``snake_case``.

    Parameters
    ----------
    :class:`str`
        ``camelCase`` string to convert to ``snake_case``.

    Returns
    -------
    :class:`str`
        ``snake_case`` string.
    """
    return CAMEL_TO_SNAKE.sub(lower_first_group, string).lower()


def snake_to_camel(string: str) -> str:
    """Convert ``string`` from ``snake_case`` to ``camelCase``.

    Parameters
    ----------
    :class:`str`
        ``snake_case`` string to convert to ``camelCase``.

    Returns
    -------
    :class:`str`
        ``camelCase`` string.
    """
    return SNAKE_TO_CAMEL.sub(upper_first_group, string)


def is_camel(string: str) -> bool:
    """Check if ``string`` is in ``camelCase``.

    Parameters
    ----------
    string: :class:`str`
        String to check.

    Returns
    -------
    :class:`bool`
        Whether the string is in ``camelCase``.
    """
    return TEST_CAMEL.fullmatch(string) is not None


def is_snake(string: str) -> bool:
    """Check if ``string`` is in ``snake_case``.

    Parameters
    ----------
    string: :class:`str`
        String to check.

    Returns
    -------
    :class:`bool`
        Whether the string is in ``snake_case``.
    """
    return TEST_SNAKE.fullmatch(string) is not None


def object_count(string: AnyStr, has_header: bool = True) -> int:
    """Count amount of objects in the ``string`` by counting ``;``,
    and removing ``1`` if ``has_header``.

    Parameters
    ----------
    string: Union[:class:`bytes`, :class:`str`]
        Data to count the amount of objects in.

    has_header: :class:`bool`
        Whether given ``string`` has a header.

    Returns
    -------
    :class:`int`
        Amount of objects in the ``string``.
    """
    delim = _LEVEL_DELIM if isinstance(string, str) else _BYTE_LEVEL_DELIM
    count = string.strip(delim).count(delim) - has_header
    return 0 if count < 0 else count


ORDINAL_SUFFIXES = ("th", "st", "nd", "rd", "th")


def to_ordinal(number: int) -> str:
    """Convert ``number`` to ordinal, for example:

    +--------+----------+
    | number |  ordinal |
    +========+==========+
    | ``0``  | ``0th``  |
    +--------+----------+
    | ``1``  | ``1st``  |
    +--------+----------+
    | ``13`` | ``13th`` |
    +--------+----------+
    | ``42`` | ``42nd`` |
    +--------+----------+

    Parameters
    ----------
    number: :class:`int`
        Number to convert to ordinal.

    Returns
    -------
    :class:`str`
        Ordinal string representing the number.
    """
    suffix = ORDINAL_SUFFIXES[min(number % 10, 4)]

    if 11 <= (number % 100) <= 13:
        suffix = "th"

    return f"{number}{suffix}"
