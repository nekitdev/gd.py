from collections import namedtuple
import re

from gd import __version__

__all__ = ("VersionInfo", "make_version_details", "normal_re", "version_info")

VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")

normal_re = (
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
compiled_re = re.compile(normal_re, re.MULTILINE)


def make_version_details(ver: str) -> VersionInfo:
    match = compiled_re.match(ver)

    if match is None:
        return VersionInfo(0, 0, 0, "final", 0)

    args = {}

    for key, value in match.groupdict().items():
        if key == "split":
            continue

        elif key == "releaselevel":
            if value is None:
                value = "f"

            value = {
                "a": "alpha",
                "b": "beta",
                "rc": "candidate",
                "f": "final",
                "dev": "developer",
            }.get(value, "final")

        elif value is None:
            value = 0

        else:
            value = int(value)

        args[key] = value

    return VersionInfo(**args)


version_info = make_version_details(__version__)
