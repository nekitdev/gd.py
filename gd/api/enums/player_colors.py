from enum import Enum


class PlayerColor(Enum):
    NOT_USED = 0
    """Do not use player colors."""

    COLOR_1 = 1
    """Use player color 1."""

    COLOR_2 = 2
    """Use player color 2."""

    DEFAULT = NOT_USED
    """The default player color."""

    def is_not_used(self) -> bool:
        """Checks if the player color is
        [`NOT_USED`][gd.api.enums.player_colors.PlayerColor.NOT_USED].

        Returns:
            Whether the player color is
                [`NOT_USED`][gd.api.enums.player_colors.PlayerColor.NOT_USED].
        """
        return self is type(self).NOT_USED

    def is_used(self) -> bool:
        """The inverse of [`is_not_used`][gd.api.enums.player_colors.PlayerColor.is_not_used].

        This is equivalent to:

        ```python
        not player_color.is_not_used()
        ```

        Returns:
            Whether the player color is used.
        """
        return not self.is_not_used()

    def is_color_1(self) -> bool:
        """Checks if the player color is
        [`COLOR_1`][gd.api.enums.player_colors.PlayerColor.COLOR_1].

        Returns:
            Whether the player color is [`COLOR_1`][gd.api.enums.player_colors.PlayerColor.COLOR_1].
        """
        return self is type(self).COLOR_1

    def is_color_2(self) -> bool:
        """Checks if the player color is
        [`COLOR_2`][gd.api.enums.player_colors.PlayerColor.COLOR_2].

        Returns:
            Whether the player color is [`COLOR_2`][gd.api.enums.player_colors.PlayerColor.COLOR_2].
        """
        return self is type(self).COLOR_2

    def is_default(self) -> bool:
        """Checks if the player color is
        [`DEFAULT`][gd.api.enums.player_colors.PlayerColor.DEFAULT].

        Returns:
            Whether the player color is [`DEFAULT`][gd.api.enums.player_colors.PlayerColor.DEFAULT].
        """
        return self is type(self).DEFAULT
