from platform import machine as get_machine
from struct import calcsize as size
from sys import platform as SYSTEM_PLATFORM_STRING
from sysconfig import get_config_var as get_config_variable
from typing import Type, TypeVar

from attrs import frozen

from gd.enums import Platform
from gd.string import String
from gd.string_utils import case_fold

__all__ = (
    "ANDROID",
    "DARWIN",
    "IOS",
    "IPAD_OS",
    "LINUX",
    "MAC_OS",
    "WINDOWS",
    "SYSTEM_BITS",
    "SYSTEM_PLATFORM",
    "SYSTEM_PLATFORM_CONFIG",
    "Platform",
    "PlatformConfig",
)

USIZE = "N"

SYSTEM_BITS = size(USIZE)

SEPARATOR = "_x"

partition_separator = SEPARATOR.partition
concat_separator = SEPARATOR.join

C = TypeVar("C", bound="PlatformConfig")


@frozen()
class PlatformConfig(String):
    platform: Platform
    bits: int

    @classmethod
    def from_string(cls: Type[C], string: str) -> C:
        platform, _, bits = partition_separator(string)

        return cls(Platform.from_name(platform), int(bits))

    def to_string(self) -> str:
        parts = (case_fold(self.platform.name), str(self.bits))

        return concat_separator(parts)

    def __str__(self) -> str:
        return self.to_string()


WINDOWS_LITERAL = "win"
CYGWIN_LITERAL = "cygwin"
IPHONE_LITERAL = "iPhone"
IPAD_LITERAL = "iPad"
DARWIN_LITERAL = "darwin"
FREE_BSD_LITERAL = "freebsd"
LINUX_LITERAL = "linux"
ANDROID_LITERAL = "android"


ANDROID_API_LEVEL_NAME = "ANDROID_API_LEVEL"
ANDROID_API_LEVEL = get_config_variable(ANDROID_API_LEVEL_NAME)

if ANDROID_API_LEVEL:
    SYSTEM_PLATFORM_STRING = ANDROID_LITERAL


ANDROID = False
DARWIN = False
IOS = False
IPAD_OS = False
MAC_OS = False
LINUX = False
WINDOWS = False


if SYSTEM_PLATFORM_STRING.startswith((WINDOWS_LITERAL, CYGWIN_LITERAL)):
    WINDOWS = True

elif SYSTEM_PLATFORM_STRING.startswith(DARWIN_LITERAL):
    DARWIN = True

    MACHINE = get_machine()

    if MACHINE.startswith(IPHONE_LITERAL):
        IOS = True

    elif MACHINE.startswith(IPAD_LITERAL):
        IPAD_OS = True

    else:
        MAC_OS = True

elif SYSTEM_PLATFORM_STRING.startswith((LINUX_LITERAL, FREE_BSD_LITERAL)):
    LINUX = True

elif SYSTEM_PLATFORM_STRING.startswith(ANDROID_LITERAL):
    ANDROID = True


SYSTEM_PLATFORM = {
    ANDROID: Platform.ANDROID,
    IOS: Platform.IOS,
    IPAD_OS: Platform.IPAD_OS,
    LINUX: Platform.LINUX,
    MAC_OS: Platform.MAC_OS,
    WINDOWS: Platform.WINDOWS,
}.get(True, Platform.UNKNOWN)


SYSTEM_PLATFORM_CONFIG = PlatformConfig(SYSTEM_PLATFORM, SYSTEM_BITS)
