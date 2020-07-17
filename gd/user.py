from gd.typing import Optional

from gd.abstractuser import AbstractUser
from gd.colors import colors
from gd.iconset import IconSet

from gd.typing import Client, User, UserStats

from gd.utils.converter import Converter
from gd.utils.enums import (
    IconType,
    StatusLevel,
    MessagePolicyType,
    FriendRequestPolicyType,
    CommentPolicyType,
)
from gd.utils.indexer import Index
from gd.utils.parser import ExtDict
from gd.utils.text_tools import make_repr


class UserStats(AbstractUser):
    """Class that extends :class:`.AbstractUser`, adding
    user's statistics to it.
    """

    def __repr__(self) -> str:
        info = {
            "account_id": self.account_id,
            "name": repr(self.name),
            "id": self.id,
            "place": Converter.to_ordinal(self.place),
            "stars": self.stars,
            "demons": self.demons,
            "cp": self.cp,
        }
        return make_repr(self, info)

    @classmethod
    def from_data(cls, data: ExtDict, client: Client) -> UserStats:
        return cls(
            account_id=data.getcast(Index.USER_ACCOUNT_ID, 0, int),
            name=data.get(Index.USER_NAME, "unknown"),
            id=data.getcast(Index.USER_PLAYER_ID, 0, int),
            stars=data.getcast(Index.USER_STARS, 0, int),
            demons=data.getcast(Index.USER_DEMONS, 0, int),
            cp=data.getcast(Index.USER_CREATOR_POINTS, 0, int),
            diamonds=data.getcast(Index.USER_DIAMONDS, 0, int),
            coins=data.getcast(Index.USER_COINS, 0, int),
            secret_coins=data.getcast(Index.USER_SECRET_COINS, 0, int),
            place=data.getcast(Index.USER_TOP_PLACE, 0, int),
            client=client,
        )

    @property
    def stars(self) -> int:
        """:class:`int`: Amount of stars the user has."""
        return self.options.get("stars", 0)

    @property
    def demons(self) -> int:
        """:class:`int`: Amount of demons the user has beaten."""
        return self.options.get("demons", 0)

    @property
    def cp(self) -> int:
        """:class:`int`: Amount of Creator Points the user has."""
        return self.options.get("cp", 0)

    @property
    def diamonds(self) -> int:
        """:class:`int`: Amount of diamonds the user has."""
        return self.options.get("diamonds", 0)

    @property
    def coins(self) -> int:
        """:class:`int`: Number of coins the user has."""
        return self.options.get("secret_coins", 0)

    @property
    def user_coins(self) -> int:
        """:class:`int`: Amount of User Coins user has."""
        return self.options.get("coins", 0)

    @property
    def place(self) -> int:
        """:class:`int`: User's place in leaderboard. ``0`` if not set."""
        return self.options.get("place", 0)

    def has_cp(self) -> bool:
        """:class:`bool`: Indicates if a user has Creator Points."""
        return self.cp > 0

    def set_place(self, place: int = 0) -> None:
        """Set the ``self.place`` to ``place`` argument."""
        self.options.update(place=place)

    async def update(self) -> None:
        """|coro|

        Update ``self``.
        """
        new = await self.client.fetch_user(self.account_id, stats=True)

        new.set_place(self.place)

        self.options = new.options


class User(UserStats):
    """Class that represents a Geometry Dash User.
    This class is derived from :class:`.UserStats`.
    """

    def __repr__(self) -> str:
        info = {
            "account_id": self.account_id,
            "id": self.id,
            "name": repr(self.name),
            "role": self.role,
            "cp": self.cp,
        }
        return make_repr(self, info)

    @classmethod
    def from_data(cls, data: ExtDict, client: Client) -> User:
        youtube = data.get(Index.USER_YOUTUBE, "")
        youtube = {"normal": youtube, "link": "https://www.youtube.com/channel/" + youtube}
        twitter = data.get(Index.USER_TWITTER, "")
        twitter = {"normal": twitter, "link": "https://twitter.com/" + twitter}
        twitch = data.get(Index.USER_TWITCH, "")
        twitch = {"normal": twitch, "link": "https://twitch.tv/" + twitch}

        return cls(
            name=data.get(Index.USER_NAME, "unknown"),
            id=data.getcast(Index.USER_PLAYER_ID, 0, int),
            stars=data.getcast(Index.USER_STARS, 0, int),
            demons=data.getcast(Index.USER_DEMONS, 0, int),
            secret_coins=data.getcast(Index.USER_SECRET_COINS, 0, int),
            coins=data.getcast(Index.USER_COINS, 0, int),
            cp=data.getcast(Index.USER_CREATOR_POINTS, 0, int),
            diamonds=data.getcast(Index.USER_DIAMONDS, 0, int),
            role=data.getcast(Index.USER_ROLE, 0, int),
            global_rank=data.getcast(Index.USER_GLOBAL_RANK, None, int),
            account_id=data.getcast(Index.USER_ACCOUNT_ID, 0, int),
            youtube=youtube,
            twitter=twitter,
            twitch=twitch,
            message_policy=MessagePolicyType.from_value(
                data.getcast(Index.USER_PRIVATE_MESSAGE_POLICY, 0, int), 0
            ),
            friend_request_policy=FriendRequestPolicyType.from_value(
                data.getcast(Index.USER_FRIEND_REQUEST_POLICY, 0, int), 0
            ),
            comment_policy=CommentPolicyType.from_value(
                data.getcast(Index.USER_COMMENT_HISTORY_POLICY, 0, int), 0
            ),
            icon_setup=IconSet(
                main_icon=data.getcast(Index.USER_ICON, 1, int),
                color_1=colors[data.getcast(Index.USER_COLOR_1, 0, int)],
                color_2=colors[data.getcast(Index.USER_COLOR_2, 0, int)],
                main_icon_type=IconType.from_value(data.getcast(Index.USER_ICON_TYPE, 0, int), 0),
                has_glow_outline=bool(data.getcast(Index.USER_GLOW_OUTLINE_2, 0, int)),
                icon_cube=data.getcast(Index.USER_ICON_CUBE, 1, int),
                icon_ship=data.getcast(Index.USER_ICON_SHIP, 1, int),
                icon_ball=data.getcast(Index.USER_ICON_BALL, 1, int),
                icon_ufo=data.getcast(Index.USER_ICON_UFO, 1, int),
                icon_wave=data.getcast(Index.USER_ICON_WAVE, 1, int),
                icon_robot=data.getcast(Index.USER_ICON_ROBOT, 1, int),
                icon_spider=data.getcast(Index.USER_ICON_SPIDER, 1, int),
                icon_explosion=data.getcast(Index.USER_EXPLOSION, 1, int),
                client=client,
            ),
            client=client,
        )

    @property
    def role(self) -> StatusLevel:
        """:class:`.StatusLevel`: A status level of the user."""
        return StatusLevel.from_value(self.options.get("role", 0))

    @property
    def rank(self) -> Optional[int]:
        """Optional[:class:`int`]: A global rank of the user.
        ``None`` if the user is not on the leaderboard.
        """
        return self.options.get("global_rank")

    @property
    def youtube(self) -> str:
        """:class:`str`: A youtube name of the user."""
        return self.options.get("youtube", {}).get("normal", "")

    @property
    def youtube_link(self) -> str:
        """:class:`str`: A link to the user's youtube channel."""
        return self.options.get("youtube", {}).get("link", "")

    @property
    def twitter(self) -> str:
        """:class:`str`: A twitter name of the user."""
        return self.options.get("twitter", {}).get("normal", "")

    @property
    def twitter_link(self) -> str:
        """:class:`str`: A link to the user's twitter page."""
        return self.options.get("twitter", {}).get("link", "")

    @property
    def twitch(self) -> str:
        """:class:`str`: A twitch name of the user."""
        return self.options.get("twitch", {}).get("normal", "")

    @property
    def twitch_link(self) -> str:
        """:class:`str`: A link to the user's twitch channel."""
        return self.options.get("twitch", {}).get("link", "")

    @property
    def message_policy(self) -> MessagePolicyType:
        """:class:`.MessagePolicyType`: A type indicating user's message inbox policy."""
        return MessagePolicyType.from_value(self.options.get("message_policy", 0))

    @property
    def friend_request_policy(self) -> FriendRequestPolicyType:
        """:class:`.FriendRequestPolicyType`: A type indicating user's friend requests policy."""
        return FriendRequestPolicyType.from_value(self.options.get("friend_request_policy", 0))

    @property
    def comment_policy(self) -> CommentPolicyType:
        """:class:`.CommentPolicyType`: A type indicating user's comment history policy."""
        return CommentPolicyType.from_value(self.options.get("comment_policy", 0))

    @property
    def icon_set(self) -> IconSet:
        """:class:`.IconSet`: An iconset of the user."""
        return self.options.get("icon_setup", IconSet(client=self.client))

    def is_mod(self, elder: Optional[str] = None) -> bool:
        """:class:`bool`: Indicates if a user is Geometry Dash (Elder) Moderator.
        For instance, *RobTop* is an Elder Moderator, that means:
        ``robtop.is_mod() -> True`` and ``robtop.is_mod('elder') -> True``.
        """
        if self.role is None:  # pragma: no cover
            return False

        elif elder is None:
            return self.role.value >= 1

        elif elder == "elder":
            return self.role.value == 2

        raise TypeError("is_mod(elder) expected elder=='elder', or None.")  # pragma: no cover

    async def update(self) -> None:
        """|coro|

        Update the user's statistics and other parameters.
        """
        new = await self.client.get_user(self.account_id)
        self.options = new.options
