import platform  # machine
import struct  # bitness
import sys  # platform
import sysconfig  # config vars

from gd.enums import Platform
from gd.typing import Tuple, cast

__all__ = (
    "ANDROID",
    "DARWIN",
    "IOS",
    "LINUX",
    "MACOS",
    "WINDOWS",
    "Platform",
    "platform_from_string",
    "platform_to_string",
    "system_bits",
    "system_platform",
    "system_platform_raw",
)

_DELIM = "_x"


def platform_from_string(string: str) -> Tuple[int, Platform]:
    platform_string, delim, bits_string = string.partition(_DELIM)

    if not delim:
        raise ValueError(f"Can not parse {string!r} to platform.")

    return int(bits_string), Platform.from_name(platform_string)


def platform_to_string(bits: int, platform: Platform) -> str:
    return f"{platform.name.casefold()}{_DELIM}{bits}"


_ANDROID_API_LEVEL = sysconfig.get_config_vars().get("ANDROID_API_LEVEL")

if _ANDROID_API_LEVEL is None:
    _ANDROID_API_LEVEL = 0

if _ANDROID_API_LEVEL > 0:
    sys.platform = "android"

_IOS_PREFIXES = ("iPad", "iPhone", "iPod")

_MACHINE = platform.machine()


ANDROID = False
DARWIN = False
IOS = False
LINUX = False
MACOS = False
WINDOWS = False


system_platform_raw = sys.platform


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
