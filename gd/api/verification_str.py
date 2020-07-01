from collections import UserList
import re

from attr import attrib, dataclass

from gd.typing import Generator, Union, ref
from gd.utils.text_tools import make_repr

__all__ = (
    "ENTRY_PATTERN",
    "Entry",
    "EntryArray",
    "iter_entries",
    "list_entries",
)

EntryType = ref("gd.api.verification_str.Entry")
Match = type(re.match("", ""))
Number = Union[float, int]


def number_from_str(string: str) -> Number:
    number = float(string)
    return int(number) if number.is_integer() else number


# [1;]n[.m];[1];[;]
ENTRY_PATTERN = re.compile(
    r"(?:(?P<prev>1);)?"  # [1;]
    r"(?P<time>[0-9]+(?:\.[0-9]*)?);"  # n[.m];
    r"(?P<next>1)?;"  # [1];
    r"(?P<dual>;)?"  # [;]
)

PATTERN_TYPES = {"time": number_from_str, "prev": bool, "next": bool, "dual": bool}


@dataclass
class Entry:
    time: Number = attrib(default=0)
    prev: bool = attrib(default=False)
    next: bool = attrib(default=False)
    dual: bool = attrib(default=False)

    def __repr__(self) -> None:
        info = {"time": self.time, "prev": self.prev, "next": self.next, "dual": self.dual}
        return make_repr(self, info)

    def dump(self) -> str:
        def gen(self) -> Generator[str, None, None]:
            if self.prev:
                yield "1;"

            yield f"{self.time};"

            if self.next:
                yield "1"

            yield ";"

            if self.dual:
                yield ";"

        return "".join(gen(self))

    @classmethod
    def from_string(cls, string: str) -> EntryType:
        match = ENTRY_PATTERN.match(string)

        if match:
            return cls.from_match(match)
        else:
            raise ValueError(
                f"Pattern {ENTRY_PATTERN.pattern} is not matched by the string: {string!r}"
            )

    @classmethod
    def from_match(cls, match: Match) -> EntryType:
        group_dict = match.groupdict()

        init_dict = {key: func(group_dict[key]) for key, func in PATTERN_TYPES.items()}

        return cls(**init_dict)


class EntryArray(UserList):
    def dump(self) -> str:
        return "".join(entry.dump() for entry in self)


def iter_entries(string: str) -> Generator[Entry, None, None]:
    yield from map(Entry.from_match, ENTRY_PATTERN.finditer(string))


def list_entries(string: str) -> EntryArray:
    return EntryArray(iter_entries(string))
