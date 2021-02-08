import os  # environment
import platform  # machine
import struct  # bitness
import sys  # platform

from gd.enums import Platform
from gd.typing import cast

__all__ = (
    "ANDROID",
    "DARWIN",
    "IOS",
    "LINUX",
    "MACOS",
    "WINDOWS",
    "Platform",
    "system_bits",
    "system_platform",
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
