from struct import calcsize as size
from sys import platform as SYSTEM_PLATFORM_STRING
from sysconfig import get_config_var as get_config_variable
from typing import Type, TypeVar

from attrs import define

from gd.binary_constants import BITS
from gd.enums import Platform
from gd.string import String
from gd.string_utils import case_fold
from gd.typing import Nullary

__all__ = (
    "ANDROID",
    "DARWIN",
    "LINUX",
    "WINDOWS",
    "SYSTEM_BITS",
    "SYSTEM_PLATFORM",
    "Platform",
    "PlatformConfig",
)

USIZE = "N"

SYSTEM_BITS = size(USIZE) * BITS

SEPARATOR = "_x"

partition_separator = SEPARATOR.partition
concat_separator = SEPARATOR.join

C = TypeVar("C", bound="PlatformConfig")

DEFAULT_BITS = 0


@define()
class PlatformConfig(String):
    platform: Platform
    bits: int = DEFAULT_BITS

    @classmethod
    def default_system(cls: Type[C]) -> C:
        return cls(SYSTEM_PLATFORM)

    @classmethod
    def system(cls: Type[C]) -> C:
        return cls(SYSTEM_PLATFORM, SYSTEM_BITS)

    @classmethod
    def default_with_platform(cls: Type[C], platform: Platform) -> C:
        return cls(platform)

    @classmethod
    def default_with_platform_factory(cls: Type[C], platform: Platform) -> Nullary[C]:
        def factory() -> C:
            return cls.default_with_platform(platform)

        return factory

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
