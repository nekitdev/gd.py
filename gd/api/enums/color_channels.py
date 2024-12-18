from enum import Enum

__all__ = ("SpecialColorChannel",)


class SpecialColorChannel(Enum):
    """Represents special color channels."""

    BACKGROUND = 1000
    """Background color channel."""

    GROUND = 1001
    """Ground color channel."""

    LINE = 1002
    """Line color channel."""

    LINE_3D = 1003
    """3D line color channel."""

    OBJECT = 1004
    """Object color channel."""

    PLAYER_1 = 1005
    """Player color 1 channel."""

    PLAYER_2 = 1006
    """Player color 2 channel."""

    LIGHT_BACKGROUND = 1007
    """Light background color channel."""

    SECONDARY_GROUND = 1009
    """Secondary ground color channel."""

    BLACK = 1010
    """Black color channel."""

    WHITE = 1011
    """White color channel."""

    LIGHTER = 1012
    """Lighter color channel."""

    MIDDLEGROUND = 1013
    """Middleground color channel."""

    SECONDARY_MIDDLEGROUND = 1014
    """Secondary middleground color channel."""

    @property
    def id(self) -> int:
        return self.value


class LegacyColorChannel(Enum):
    DEFAULT = 0
    PLAYER_1 = 1
    PLAYER_2 = 2
    COLOR_1 = 3
    COLOR_2 = 4
    LIGHT_BACKGROUND = 5
    COLOR_3 = 6
    COLOR_4 = 7
    LINE_3D = 8

    def migrate(self) -> int:
        return LEGACY_COLOR_CHANNEL_TO_COLOR_CHANNEL_ID[self]


DEFAULT_CHANNEL_ID = 0
COLOR_1_CHANNEL_ID = 1
COLOR_2_CHANNEL_ID = 2
COLOR_3_CHANNEL_ID = 3
COLOR_4_CHANNEL_ID = 4


LEGACY_COLOR_CHANNEL_TO_COLOR_CHANNEL_ID = {
    LegacyColorChannel.DEFAULT: DEFAULT_CHANNEL_ID,
    LegacyColorChannel.PLAYER_1: SpecialColorChannel.PLAYER_1.id,
    LegacyColorChannel.PLAYER_2: SpecialColorChannel.PLAYER_2.id,
    LegacyColorChannel.COLOR_1: COLOR_1_CHANNEL_ID,
    LegacyColorChannel.COLOR_2: COLOR_2_CHANNEL_ID,
    LegacyColorChannel.LIGHT_BACKGROUND: SpecialColorChannel.LIGHT_BACKGROUND.id,
    LegacyColorChannel.COLOR_3: COLOR_3_CHANNEL_ID,
    LegacyColorChannel.COLOR_4: COLOR_4_CHANNEL_ID,
    LegacyColorChannel.LINE_3D: SpecialColorChannel.LINE_3D.id,
}
