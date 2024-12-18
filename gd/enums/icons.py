from enum import Enum

from gd.strings.case_folding import case_fold

__all__ = ("IconType",)


class IconType(Enum):
    """Represents icon types."""

    CUBE = 0
    """Cube icons."""

    SHIP = 1
    """Ship icons."""

    BALL = 2
    """Ball icons."""

    UFO = 3
    """UFO icons."""

    WAVE = 4
    """Wave icons."""

    ROBOT = 5
    """Robot icons."""

    SPIDER = 6
    """Spider icons."""

    SWING = 7
    """Swing icons."""

    JETPACK = 8
    """Jetpack icons."""

    DEFAULT = CUBE
    """The default icon type."""

    def is_cube(self) -> bool:
        """Checks if the icon type is [`CUBE`][gd.enums.icons.IconType.CUBE].

        Returns:
            Whether the icon type is [`CUBE`][gd.enums.icons.IconType.CUBE].
        """
        return self is type(self).CUBE

    def is_ship(self) -> bool:
        """Checks if the icon type is [`SHIP`][gd.enums.icons.IconType.SHIP].

        Returns:
            Whether the icon type is [`SHIP`][gd.enums.icons.IconType.SHIP].
        """
        return self is type(self).SHIP

    def is_ball(self) -> bool:
        """Checks if the icon type is [`BALL`][gd.enums.icons.IconType.BALL].

        Returns:
            Whether the icon type is [`BALL`][gd.enums.icons.IconType.BALL].
        """
        return self is type(self).BALL

    def is_ufo(self) -> bool:
        """Checks if the icon type is [`UFO`][gd.enums.icons.IconType.UFO].

        Returns:
            Whether the icon type is [`UFO`][gd.enums.icons.IconType.UFO].
        """
        return self is type(self).UFO

    def is_wave(self) -> bool:
        """Checks if the icon type is [`WAVE`][gd.enums.icons.IconType.WAVE].

        Returns:
            Whether the icon type is [`WAVE`][gd.enums.icons.IconType.WAVE].
        """
        return self is type(self).WAVE

    def is_robot(self) -> bool:
        """Checks if the icon type is [`ROBOT`][gd.enums.icons.IconType.ROBOT].

        Returns:
            Whether the icon type is [`ROBOT`][gd.enums.icons.IconType.ROBOT].
        """
        return self is type(self).ROBOT

    def is_spider(self) -> bool:
        """Checks if the icon type is [`SPIDER`][gd.enums.icons.IconType.SPIDER].

        Returns:
            Whether the icon type is [`SPIDER`][gd.enums.icons.IconType.SPIDER].
        """
        return self is type(self).SPIDER

    def is_swing(self) -> bool:
        """Checks if the icon type is [`SWING`][gd.enums.icons.IconType.SWING].

        Returns:
            Whether the icon type is [`SWING`][gd.enums.icons.IconType.SWING].
        """
        return self is type(self).SWING

    def is_jetpack(self) -> bool:
        """Checks if the icon type is [`JETPACK`][gd.enums.icons.IconType.JETPACK].

        Returns:
            Whether the icon type is [`JETPACK`][gd.enums.icons.IconType.JETPACK].
        """
        return self is type(self).JETPACK

    def is_default(self) -> bool:
        """Checks if the icon type is [`DEFAULT`][gd.enums.icons.IconType.DEFAULT].

        Returns:
            Whether the icon type is [`DEFAULT`][gd.enums.icons.IconType.DEFAULT].
        """
        return self is type(self).DEFAULT

    @property
    def case_fold_name(self) -> str:
        return case_fold(self.name)
