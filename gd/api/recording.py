import re

from gd.text_utils import concat, make_repr
from gd.typing import Iterable, Iterator, List, Match, Union

__all__ = (
    "RECORD_ENTRY_PATTERN",
    "RecordEntry",
    "iter_record_entries",
    "list_record_entries",
    "dump_record_entries",
)

# [1;]n[.m];[1];[;]
RECORD_ENTRY_PATTERN = re.compile(
    r"(?:(?P<prev>1);)?"  # [1;]
    r"(?P<time>[0-9]+(?:\.[0-9]*)?);"  # n[.m];
    r"(?P<next>1)?;"  # [1];
    r"(?P<dual>;)?"  # [;]
)

PATTERN_TYPES = {"time": float, "prev": bool, "next": bool, "dual": bool}


def _truncate_if_int(value: float) -> Union[float, int]:
    truncated = int(value)
    return value if value != truncated else truncated


def _entry_string_generator(entry: "RecordEntry") -> Iterator[str]:
    if entry.prev:
        yield "1;"

    yield f"{_truncate_if_int(entry.time)};"

    if entry.next:
        yield "1"

    yield ";"

    if entry.dual:
        yield ";"


class RecordEntry:
    def __init__(
        self, time: float = 0.0, prev: bool = False, next: bool = False, dual: bool = False,
    ) -> None:
        self._time = time
        self._prev = prev
        self._next = next
        self._dual = dual

    def __repr__(self) -> str:
        info = {
            "time": self.time,
            "prev": self.prev,
            "next": self.next,
            "dual": self.dual,
        }

        return make_repr(self, info)

    @property
    def time(self) -> float:
        """Time delta from the start of the level until this entry."""
        return self._time

    @property
    def prev(self) -> bool:
        """Whether input was previously activated."""
        return self._prev

    @property
    def next(self) -> bool:
        """Whether input should be activated."""
        return self._next

    @property
    def dual(self) -> bool:
        """Whether input should be applied to the second player, and not first."""
        return self._dual

    @classmethod
    def from_string(cls, string: str) -> "RecordEntry":
        """Create record entry from string."""
        match = RECORD_ENTRY_PATTERN.match(string)

        if match is None:
            raise ValueError(
                f"Pattern {RECORD_ENTRY_PATTERN.pattern} is not matched by the string: {string!r}"
            )

        return cls.from_match(match)

    def to_string(self) -> str:
        return concat(_entry_string_generator(self))

    @classmethod
    def from_match(cls, match: Match) -> "RecordEntry":
        """Create record from a regular expression match. Intended for internal use."""
        group_dict = match.groupdict()

        init_dict = {key: func(group_dict[key]) for key, func in PATTERN_TYPES.items()}

        return cls(**init_dict)  # type: ignore


def iter_record_entries(string: str) -> Iterator[RecordEntry]:
    """Return an iterator over record entries, constructed from the string."""
    yield from map(RecordEntry.from_match, RECORD_ENTRY_PATTERN.finditer(string))


def list_record_entries(string: str) -> List[RecordEntry]:
    """Same as :func:`~gd.api.iter_record_entries`, but returns a list instead."""
    return list(iter_record_entries(string))


def dump_record_entries(entries: Iterable[RecordEntry]) -> str:
    """Dump iterable of record entries to string."""
    return concat(map(RecordEntry.to_string, entries))
