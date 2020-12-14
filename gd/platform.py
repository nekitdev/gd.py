import os  # environment
import platform  # machine
import struct  # bitness
import sys  # platform

from attr import attrib, dataclass

from gd.enums import Platform
from gd.typing import Union, cast

__all__ = (
    "ANDROID",
    "DARWIN",
    "IOS",
    "LINUX",
    "MACOS",
    "WINDOWS",
    "Platform",
    "PlatformPair",
    "byte_bits",
    "platform_pair",
    "system_bits",
    "system_platform",
    "system_platform_pair",
    "system_platform_raw",
)

_DELIM = "_x"


_ANDROID_ARGUMENT = "ANDROID_ARGUMENT"
_IOS_PREFIXES = ("iPad", "iPhone", "iPod")

_ENVIRONMENT = os.environ
_MACHINE = platform.machine()


ANDROID = False
DARWIN = False
IOS = False
LINUX = False
MACOS = False
WINDOWS = False


system_platform_raw = sys.platform


if _ANDROID_ARGUMENT in _ENVIRONMENT:
    system_platform_raw = "android"

if system_platform_raw.startswith(("win", "cygwin")):
    WINDOWS = True

elif system_platform_raw.startswith("darwin"):
    DARWIN = True

    if _MACHINE.startswith(_IOS_PREFIXES):
        IOS = True

    else:
        MACOS = True

elif system_platform_raw.startswith(("freebsd", "linux")):
    LINUX = True

elif system_platform_raw.startswith("android"):
    ANDROID = True


system_platform = cast(
    Platform, {
        ANDROID: Platform.ANDROID,
        IOS: Platform.IOS,
        LINUX: Platform.LINUX,
        MACOS: Platform.MACOS,
        WINDOWS: Platform.WINDOWS,
    }.get(True, Platform.UNKNOWN),
)


byte_bits = 8
system_bits = struct.calcsize("P") * byte_bits


def platform_from_value(value: Union[str, Platform]) -> Platform:
    return Platform.from_value(value)


@dataclass(repr=False)
class PlatformPair:
    platform: Platform = attrib(converter=platform_from_value, default=system_platform)
    bits: int = attrib(converter=int, default=system_bits)

    def __repr__(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_string(cls, string: str) -> "PlatformPair":
        platform_string, delim, bits_string = string.partition(_DELIM)

        if not delim:
            raise ValueError(f"Can not convert {string!r} to platform pair.")

        return cls(platform_string, bits_string)

    def to_string(self) -> str:
        return f"{self.platform.name.casefold()}{_DELIM}{self.bits}"


platform_pair = PlatformPair


system_platform_pair = platform_pair(system_platform, system_bits)
