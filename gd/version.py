import re
import sys
from collections import namedtuple

from gd import __version__
from gd.typing import Optional, Union

__all__ = (
    "VersionInfo",
    "create_version_info",
    "make_version_info",
    "python_version_info",
    "version_info",
)

short_to_long_names = {
    "a": "alpha",
    "b": "beta",
    "rc": "candidate",
    "dev": "developer",
    "f": "final",
}
long_to_short_names = {
    long_name: short_name for short_name, long_name in short_to_long_names.items()
}

default_level = "final"

version_parts = {"major", "minor", "micro", "release_level", "serial"}

version_re = (
    r"^\s*(?:"
    r"(?P<major>[0-9]+)"
    r"(?P<split>[\.-])?"
    r"(?P<minor>[0-9]+)?"
    r"(?P=split)?"
    r"(?P<micro>[0-9]+)?"
    r"(?P<release_level>a|b|rc|f|dev)?"
    r"(?P<serial>[0-9]+)?"
    r")\s*$"
)

compiled_re = re.compile(version_re, re.MULTILINE)

release_level_literal = "release_level"


def parse_value(key: str, value: Optional[str]) -> Union[int, str]:
    if key == release_level_literal:
        if value is None:
            return default_level

        return short_to_long_names.get(value, default_level)

    return 0 if value is None else int(value)


class VersionInfo(namedtuple("VersionInfo", "major minor micro release_level serial")):
    """Named tuple that represents version info, similar to :obj:`sys.version_info`.

    .. container:: operations

        .. describe:: str(v)

            Return human-friendly version format.
            For example, ``VersionInfo(1, 0, 0, "alpha", 1)`` is ``1.0.0a1``.
    """

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_string(cls, version: str) -> "VersionInfo":
        """Create :class:`~gd.VersionInfo` from ``version`` string."""
        match = compiled_re.match(version)

        if match is None:
            raise ValueError(f"Given version, {version!r}, is not valid.")

        parts = {
            key: parse_value(key, value)
            for key, value in match.groupdict().items()
            if key in version_parts
        }

        return cls(**parts)  # type: ignore

    @property  # type: ignore
    def release_letter(self) -> str:
        return long_to_short_names.get(self.release_level, "f")

    def to_string(self) -> str:
        """Convert :class:`~gd.VersionInfo` to string."""
        if self.release_level == default_level and not self.serial:
            return f"{self.major}.{self.minor}.{self.micro}"

        return f"{self.major}.{self.minor}.{self.micro}{self.release_letter}{self.serial}"

    @property
    def releaselevel(self) -> str:  # alias to be compatible with the sys.version_info
        return self.release_level


def create_version_info(string: str) -> VersionInfo:
    """Same as :meth:`~gd.VersionInfo.from_string`."""
    return VersionInfo.from_string(string)


make_version_info = create_version_info

version_info: VersionInfo = create_version_info(__version__)
python_version_info: VersionInfo = VersionInfo(*sys.version_info)
