from sys import platform as SYSTEM_PLATFORM_STRING
from sysconfig import get_config_var as get_config_variable

from gd.enums import Platform

__all__ = (
    "ANDROID",
    "DARWIN",
    "LINUX",
    "WINDOWS",
    "SYSTEM_PLATFORM",
)

WINDOWS_LITERAL = "win"
CYGWIN_LITERAL = "cygwin"

DARWIN_LITERAL = "darwin"

FREE_BSD_LITERAL = "freebsd"
LINUX_LITERAL = "linux"

ANDROID_LITERAL = "android"


ANDROID_API_LEVEL_NAME = "ANDROID_API_LEVEL"
ANDROID_API_LEVEL = get_config_variable(ANDROID_API_LEVEL_NAME)

if ANDROID_API_LEVEL:
    SYSTEM_PLATFORM_STRING = ANDROID_LITERAL  # noqa


ANDROID = False
DARWIN = False
LINUX = False
WINDOWS = False


if SYSTEM_PLATFORM_STRING.startswith((WINDOWS_LITERAL, CYGWIN_LITERAL)):
    WINDOWS = True

elif SYSTEM_PLATFORM_STRING.startswith(DARWIN_LITERAL):
    DARWIN = True

elif SYSTEM_PLATFORM_STRING.startswith((LINUX_LITERAL, FREE_BSD_LITERAL)):
    LINUX = True

elif SYSTEM_PLATFORM_STRING.startswith(ANDROID_LITERAL):
    ANDROID = True


SYSTEM_PLATFORM = {
    ANDROID: Platform.ANDROID,
    DARWIN: Platform.DARWIN,
    LINUX: Platform.LINUX,
    WINDOWS: Platform.WINDOWS,
}.get(True, Platform.UNKNOWN)
