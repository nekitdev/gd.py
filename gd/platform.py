from struct import calcsize as size
from sys import platform as SYSTEM_PLATFORM_STRING
from sysconfig import get_config_var as get_config_variable
from typing import Type, TypeVar

from attrs import define
from typing_aliases import Nullary

from gd.binary_constants import BITS
from gd.enums import Platform
from gd.string_utils import case_fold

__all__ = (
    "ANDROID",
    "DARWIN",
    "LINUX",
    "WINDOWS",
    "SYSTEM_PLATFORM",
    "SYSTEM_BITS",
    "SYSTEM_PLATFORM_CONFIG",
)

USIZE = "N"
USIZE_SIZE = size(USIZE)
USIZE_BITS = USIZE_SIZE * BITS

SYSTEM_BITS = USIZE_BITS


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


DEFAULT_BITS = 0

SEPARATOR = "_x"
concat_separator = SEPARATOR.join

PC = TypeVar("PC", bound="PlatformConfig")


@define()
class PlatformConfig:
    platform: Platform = Platform.DEFAULT
    bits: int = DEFAULT_BITS

    @classmethod
    def system(cls: Type[PC]) -> PC:
        return cls(SYSTEM_PLATFORM, SYSTEM_BITS)

    @classmethod
    def default_with_platform(cls: Type[PC], platform: Platform) -> PC:
        return cls(platform)

    @classmethod
    def default_with_platform_factory(cls: Type[PC], platform: Platform) -> Nullary[PC]:
        def factory() -> PC:
            return cls.default_with_platform(platform)

        return factory

    def __hash__(self) -> int:
        return hash(type(self)) ^ hash(self.platform) ^ hash(self.bits)

    @classmethod
    def from_string(cls: Type[PC], string: str) -> PC:
        platform_string, bits_string = string.split(SEPARATOR)

        platform = Platform[platform_string.upper()]
        bits = int(bits_string)

        return cls(platform, bits)

    def to_string(self) -> str:
        values = (case_fold(self.platform.name), str(self.bits))

        return concat_separator(values)

    def __str__(self) -> str:
        return self.to_string()


SYSTEM_PLATFORM_CONFIG = PlatformConfig.system()
