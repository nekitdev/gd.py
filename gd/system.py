"""System configuration."""

from __future__ import annotations

from enum import Enum
from platform import system
from struct import calcsize as size
from typing import Literal

from attrs import evolve, frozen
from typing_aliases import Nullary
from typing_extensions import Self

from gd.binary.constants import SIZE_BITS
from gd.strings.case_folding import case_fold

__all__ = (
    # types
    "Platform",
    "Config",
    # bitness
    "BITS",
    # platform
    "PLATFORM",
    # config
    "CONFIG",
    # flags
    "DARWIN",
    "LINUX",
    "WINDOWS",
    "UNKNOWN",
)


class Platform(Enum):
    """Represents platforms."""

    UNKNOWN = "unknown"
    """Unknown platform."""

    DARWIN = "darwin"
    """Darwin platform."""

    LINUX = "linux"
    """Linux platform."""

    WINDOWS = "windows"
    """Windows platform."""

    DEFAULT = UNKNOWN
    """Default platform."""

    @classmethod
    def from_string(cls, string: str) -> Platform:
        """Returns the platform that corresponds to the `string`.

        This function is case-insensitive, meaning `linux` and `Linux` both correspond
        to [`LINUX`][gd.system.Platform.LINUX].

        If the `string` does not correspond to any platform, [`UNKNOWN`][gd.system.Platform.UNKNOWN]
        is returned.

        Arguments:
            string: The string to find the corresponding platform for.

        Returns:
            The platform that corresponds to the given string.
        """
        try:
            return cls(case_fold(string))

        except ValueError:
            return cls.UNKNOWN

    @classmethod
    def of_system(cls) -> Platform:
        """Returns the platform of the current system.

        This function is equivalent to calling [`from_string`][gd.system.Platform.from_string]
        with the result of [`platform.system`][platform.system].

        Returns:
            The platform of the current system.
        """
        return cls.from_string(system())

    def is_unknown(self) -> bool:
        """Checks if the platform is [`UNKNOWN`][gd.system.Platform.UNKNOWN].

        Returns:
            Whether the platform is [`UNKNOWN`][gd.system.Platform.UNKNOWN].
        """
        return self is type(self).UNKNOWN

    def is_darwin(self) -> bool:
        """Checks if the platform is [`DARWIN`][gd.system.Platform.DARWIN].

        Returns:
            Whether the platform is [`DARWIN`][gd.system.Platform.DARWIN].
        """
        return self is type(self).DARWIN

    def is_linux(self) -> bool:
        """Checks if the platform is [`LINUX`][gd.system.Platform.LINUX].

        Returns:
            Whether the platform is [`LINUX`][gd.system.Platform.LINUX].
        """
        return self is type(self).LINUX

    def is_windows(self) -> bool:
        """Checks if the platform is [`WINDOWS`][gd.system.Platform.WINDOWS].

        Returns:
            Whether the platform is [`WINDOWS`][gd.system.Platform.WINDOWS].
        """
        return self is type(self).WINDOWS


DEFAULT_BITS: Literal[0] = 0
"""Default bits."""

SEPARATOR = "_x"
"""The separator to use in the configuration string."""

concat = SEPARATOR.join


def concat_args(*args: str) -> str:
    return concat(args)


UNEXPECTED = "unexpected config string: `{}`"
unexpected = UNEXPECTED.format


@frozen()
class Config:
    """Represents configurations."""

    platform: Platform = Platform.DEFAULT
    """The platform of the configuration."""
    bits: int = DEFAULT_BITS
    """The bitness of the configuration."""

    @classmethod
    def of_system(cls) -> Self:
        """Constructs the configuration determined from the system.

        This is equivalent to constructing the configuration with [`PLATFORM`][gd.system.PLATFORM]
        and [`BITS`][gd.system.BITS].

        Returns:
            The configuration determined from the system.
        """
        return cls(PLATFORM, BITS)

    @classmethod
    def default(cls, platform: Platform) -> Self:
        """Constructs the configuration with the given `platform` and the default bitness.

        Arguments:
            platform: The platform to use.

        Returns:
            The configuration with the given `platform` and the default bitness.
        """
        return cls(platform)

    @classmethod
    def factory(cls, platform: Platform) -> Nullary[Self]:
        """Returns the factory function that constructs the configuration using
        [`default`][gd.system.Config.default].

        Arguments:
            platform: The platform to use.

        Returns:
            The factory function.
        """

        def default() -> Self:  # type: ignore
            return cls.default(platform)

        return default

    def with_platform(self, platform: Platform) -> Self:
        """Returns the configuration with the same bitness, but new `platform`.

        Arguments:
            platform: The new platform.

        Returns:
            The updated configuration.
        """
        return evolve(self, platform=platform)

    def with_bits(self, bits: int) -> Self:
        """Returns the configuration with the same platform, but new `bits`.

        Arguments:
            bits: The new bitness.

        Returns:
            The updated configuration.
        """
        return evolve(self, bits=bits)

    def to_string(self) -> str:
        """Returns the string representation of the configuration.

        Returns:
            The string representation of the configuration.
        """
        return concat_args(self.platform.value, str(self.bits))

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Parses the configuration from the `string`.

        The `string` must be in the format as returned by [`to_string`][gd.system.Config.to_string],
        for instance, `linux_x64`.

        Arguments:
            string: The string to parse.

        Raises:
            ValueError: If the `string` is not in the correct format.

        Returns:
            The parsed configuration.
        """
        platform_string, separator, bits_string = string.partition(SEPARATOR)

        if not separator:
            raise ValueError(unexpected(string))

        platform = Platform(platform_string)
        bits = int(bits_string)

        return cls(platform, bits)

    def __str__(self) -> str:
        return self.to_string()


# determine bitness


POINTER: Literal["P"] = "P"
"""The pointer type."""

POINTER_SIZE = size(POINTER)
"""The size of the pointer."""

POINTER_BITS = POINTER_SIZE * SIZE_BITS
"""The size of the pointer in bits."""

BITS = POINTER_BITS
"""The determined bitness."""


# determine platform


PLATFORM = Platform.of_system()
"""The determined platform."""


# determine config


CONFIG = Config.of_system()
"""The determined configuration."""


# provide flags


DARWIN = PLATFORM.is_darwin()
"""Whether the [`PLATFORM`][gd.system.PLATFORM] is [`DARWIN`][gd.system.Platform.DARWIN]."""

LINUX = PLATFORM.is_linux()
"""Whether the [`PLATFORM`][gd.system.PLATFORM] is [`LINUX`][gd.system.Platform.LINUX]."""

WINDOWS = PLATFORM.is_windows()
"""Whether the [`PLATFORM`][gd.system.PLATFORM] is [`WINDOWS`][gd.system.Platform.WINDOWS]."""

UNKNOWN = PLATFORM.is_unknown()
"""Whether the [`PLATFORM`][gd.system.PLATFORM] is [`UNKNOWN`][gd.system.Platform.UNKNOWN]."""
