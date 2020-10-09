from collections import namedtuple
import re
import sys

import aiohttp

from gd import __version__
from gd.typing import Optional, Union

__all__ = (
    "VersionInfo",
    "aiohttp_version",
    "make_version_info",
    "python_version",
    "version_re",
    "version_info",
)

short_to_long_names = {
    "a": "alpha",
    "b": "beta",
    "rc": "candidate",
    "f": "final",
    "dev": "developer",
}
long_to_short_names = {
    long_name: short_name for short_name, long_name in short_to_long_names.items()
}

default_level = "final"

version_parts = {"major", "minor", "micro", "releaselevel", "serial"}

version_re = (
    r"^\s*(?:"
    r"(?P<major>[0-9]+)"
    r"(?P<split>[\.-])?"
    r"(?P<minor>[0-9]+)?"
    r"(?P=split)?"
    r"(?P<micro>[0-9]+)?"
    r"(?P<releaselevel>a|b|rc|f|dev)?"
    r"(?P<serial>[0-9]+)?"
    r")\s*$"
)

compiled_re = re.compile(version_re, re.MULTILINE)


def parse_value(key: str, value: Optional[str]) -> Union[int, str]:
    if key == "releaselevel":
        if value is None:
            return default_level

        return short_to_long_names.get(value, default_level)

    return 0 if value is None else int(value)


class VersionInfo(namedtuple("VersionInfo", "major minor micro releaselevel serial")):
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

    def to_string(self) -> str:
        """Convert :class:`~gd.VersionInfo` to string."""
        short_release = long_to_short_names.get(self.releaselevel)

        return f"{self.major}.{self.minor}.{self.micro}{short_release}{self.serial}"


def make_version_info(string: str) -> VersionInfo:
    """Same as :meth:`~gd.VersionInfo.from_string`."""
    return VersionInfo.from_string(string)


version_info = make_version_info(__version__)
aiohttp_version = make_version_info(aiohttp.__version__)
python_version = VersionInfo(*sys.version_info)
