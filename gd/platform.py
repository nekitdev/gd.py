import sys
from builtins import hasattr as has_attribute
from platform import system
from struct import calcsize as size
from typing import Type, TypeVar

from attrs import evolve, frozen
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


WINDOWS_LITERAL = "Windows"

DARWIN_LITERAL = "Darwin"

LINUX_LITERAL = "Linux"

GET_ANDROID_API_LEVEL = "getandroidapilevel"

SYSTEM = system()

ANDROID = has_attribute(sys, GET_ANDROID_API_LEVEL)

DARWIN = SYSTEM == DARWIN_LITERAL

LINUX = SYSTEM == LINUX_LITERAL and not ANDROID

WINDOWS = SYSTEM == WINDOWS_LITERAL

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


@frozen()
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

    def with_platform(self: PC, platform: Platform) -> PC:
        return evolve(self, platform=platform)

    def with_bits(self: PC, bits: int) -> PC:
        return evolve(self, bits=bits)

    @classmethod
    def from_string(cls: Type[PC], string: str) -> PC:
        platform_string, separator, bits_string = string.partition(SEPARATOR)

        if not separator:
            raise ValueError  # TODO: message?

        platform = Platform[platform_string.upper()]
        bits = int(bits_string)

        return cls(platform, bits)

    def to_string(self) -> str:
        values = (case_fold(self.platform.name), str(self.bits))

        return concat_separator(values)

    def __str__(self) -> str:
        return self.to_string()


SYSTEM_PLATFORM_CONFIG = PlatformConfig.system()
