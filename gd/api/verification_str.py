import re

from gd.typing import Union, ref

EntryType = ref("gd.api.verification_str.Entry")
Number = Union[float, int]


def number_from_str(string: str) -> Number:
    number = float(string)
    return int(number) if number.is_integer() else number


# [1;]n.[m];[1];[;]
ENTRY_PATTERN = re.compile(
    r"(?:(?P<prev>1);)?"  # [1;]
    r"(?P<time>[0-9]+(?:\.[0-9]*)?);"  # n.[m];
    r"(?P<next>1)?;"  # [1];
    r"(?P<dual>;)?"  # [;]
)

PATTERN_TYPES = {"time": number_from_str, "prev": bool, "next": bool, "dual": bool}


class Entry:
    pass
