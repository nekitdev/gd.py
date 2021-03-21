# DOCUMENT

from collections import UserList as ListDerive
import re

from gd.text_utils import concat, make_repr
from gd.typing import Iterable, Iterator, Match, Type, TypeVar, Union

__all__ = (
    "RECORDING_ENTRY_PATTERN",
    "RecordingEntry",
    "Recording",
)

RecordingEntryT = TypeVar("RecordingEntryT", bound="RecordingEntry")

# [1;]n[.d];[1];[;]
RECORDING_ENTRY_PATTERN = re.compile(
    r"(?:(?P<prev>1);)?"  # [1;]
    r"(?P<time>[0-9]+(?:\.[0-9]*)?);"  # n[.d];
    r"(?P<next>1)?;"  # [1];
    r"(?P<dual>;)?"  # [;]
)

PATTERN_TYPES = {"time": float, "prev": bool, "next": bool, "dual": bool}


def _serialize_float(value: float) -> Union[float, int]:
    int_value = int(value)

    return value if value != int_value else int_value


class RecordingEntry:
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

    def to_string_iterator(self) -> Iterator[str]:
        if self.prev:
            yield "1;"

        yield f"{_serialize_float(self.time)};"

        if self.next:
            yield "1"

        yield ";"

        if self.dual:
            yield ";"

    @classmethod
    def from_string(cls: Type[RecordingEntryT], string: str) -> RecordingEntryT:
        """Create record entry from string."""
        match = RECORDING_ENTRY_PATTERN.match(string)

        if match is None:
            raise ValueError(
                f"Pattern {RECORDING_ENTRY_PATTERN.pattern} "
                f"is not matched by the string: {string!r}."
            )

        return cls.from_match(match)

    def to_string(self) -> str:
        return concat(self.to_string_iterator())

    @classmethod
    def from_match(cls: Type[RecordingEntryT], match: Match) -> RecordingEntryT:
        """Create record from a regular expression match. Intended for internal use."""
        mapping = match.groupdict()

        init_args = {
            name: function(mapping.get(name, 0)) for name, function in PATTERN_TYPES.items()
        }

        return cls(**init_args)  # type: ignore


RecordingT = TypeVar("RecordingT", bound="Recording")


class Recording(ListDerive):
    @staticmethod
    def iter_string(
        string: str, cls: Type[RecordingEntryT] = RecordingEntry  # type: ignore
    ) -> Iterator[RecordingEntryT]:
        iterator = RECORDING_ENTRY_PATTERN.finditer(string)

        yield from map(cls.from_match, iterator)

    @staticmethod
    def collect_string(
        recording: Iterable[RecordingEntryT],
        cls: Type[RecordingEntryT] = RecordingEntry,  # type: ignore
    ) -> str:
        return concat(map(cls.to_string, recording))

    @classmethod
    def from_string(cls: Type[RecordingT], string: str) -> RecordingT:
        return cls(cls.iter_string(string))

    def to_string(self, cls: Type[RecordingEntryT] = RecordingEntry) -> str:  # type: ignore
        return concat(self.collect_string(self, cls))
