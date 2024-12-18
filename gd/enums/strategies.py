from enum import Enum

__all__ = (
    "CommentStrategy",
    "LeaderboardStrategy",
    "LevelLeaderboardStrategy",
    "SearchStrategy",
)


class CommentStrategy(Enum):
    """Represents comment strategies."""

    RECENT = 0
    """Recent comments."""

    MOST_LIKED = 1
    """Most liked comments."""

    DEFAULT = RECENT
    """The default comment strategy."""


class LeaderboardStrategy(Enum):
    """Represents leaderboard strategies."""

    PLAYERS = 0
    """The players leaderboard."""

    FRIENDS = 1
    """The friends leaderboard."""

    RELATIVE = 2
    """The relative leaderboard."""

    CREATORS = 3
    """The creators leaderboard."""

    DEFAULT = PLAYERS
    """The default leaderboard strategy."""

    def requires_login(self) -> bool:
        """Checks if the strategy is in [`REQUIRE_LOGIN`][gd.enums.strategies.REQUIRE_LOGIN].

        Returns:
            Whether the strategy is in [`REQUIRE_LOGIN`][gd.enums.strategies.REQUIRE_LOGIN].
        """
        return self in REQUIRE_LOGIN


REQUIRE_LOGIN = {LeaderboardStrategy.FRIENDS, LeaderboardStrategy.RELATIVE}
"""Leaderboard strategies that require login."""


class LevelLeaderboardStrategy(Enum):
    """Represents level leaderboard strategies."""

    FRIENDS = 0
    """The friends level leaderboard."""

    ALL = 1
    """The global level leaderboard."""

    WEEKLY = 2
    """The weekly level leaderboard."""

    DEFAULT = ALL
    """The default level leaderboard strategy."""


class SearchStrategy(Enum):
    """Represents search strategies."""

    DEFAULT = 0
    """The default search strategy."""

    MOST_DOWNLOADED = 1
    """Most downloaded levels."""

    MOST_LIKED = 2
    """Most liked levels."""

    TRENDING = 3
    """Trending levels."""

    RECENT = 4
    """Recent levels."""

    USER = 5
    """Levels by user."""

    FEATURED = 6
    """Featured levels."""

    MAGIC = 7
    """Magic levels."""

    SENT = 8
    """Sent levels."""

    SELECTED = 10
    """Selected levels."""

    RATED = 11
    """Rated levels."""

    FOLLOWED = 12
    """Followed levels."""

    FRIENDS = 13
    """Levels by friends."""

    DAILY_HISTORY = 21
    """Daily levels history."""

    WEEKLY_HISTORY = 22
    """Weekly levels history."""
