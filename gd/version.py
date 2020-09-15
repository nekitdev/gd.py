from collections import namedtuple
import re
import sys

import aiohttp

from gd import __version__
from gd.typing import Optional, Union

__all__ = ("VersionInfo", "make_version_info", "python_version", "version_re", "version_info")

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
    r"(?P<major>\d+)"
    r"(?P<split>[\.-])?"
    r"(?P<minor>\d+)?"
    r"(?P=split)?"
    r"(?P<micro>\d+)?"
    r"(?P<releaselevel>a|b|rc|f|dev)?"
    r"(?P<serial>\d+)?"
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
    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_string(cls, version: str) -> "VersionInfo":
        match = compiled_re.fullmatch(version)

        if match is None:
            raise ValueError(f"Given version, {version!r}, is not valid.")

        parts = {
            key: parse_value(key, value)
            for key, value in match.groupdict().items()
            if key in version_parts
        }

        return cls(**parts)  # type: ignore

    def to_string(self) -> str:
        short_release = long_to_short_names.get(self.releaselevel)

        return f"{self.major}.{self.minor}.{self.micro}{short_release}{self.serial}"


def make_version_info(string: str) -> VersionInfo:
    return VersionInfo.from_string(string)


version_info = make_version_info(__version__)
aiohttp_version = make_version_info(aiohttp.__version__)
python_version = VersionInfo(*sys.version_info)
