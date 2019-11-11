from .abstractuser import AbstractUser
from .iconset import IconSet

from .utils.converter import Converter
from .utils.enums import (
    StatusLevel, MessagePolicyType,
    FriendRequestPolicyType, CommentPolicyType
)
from .utils.wrap_tools import make_repr

class UserStats(AbstractUser):
    """Class that extends :class:`.AbstractUser`, adding
    user's statistics to it.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    def __repr__(self):
        info = {
            'account_id': self.account_id,
            'name': repr(self.name),
            'id': self.id,
            'lb_place': Converter.to_ordinal(self.lb_place),
            'stars': self.stars,
            'demons': self.demons,
            'cp': self.cp
        }
        return make_repr(self, info)

    @property
    def stars(self):
        """:class:`int`: Amount of stars the user has."""
        return self.options.get('stars', 0)

    @property
    def demons(self):
        """:class:`int`: Amount of demons the user has beaten."""
        return self.options.get('demons', 0)

    @property
    def cp(self):
        """:class:`int`: Amount of Creator Points the user has."""
        return self.options.get('cp', 0)

    @property
    def diamonds(self):
        """:class:`int`: Amount of diamonds the user has."""
        return self.options.get('diamonds', 0)

    @property
    def coins(self):
        """:class:`int`: Number of coins the user has."""
        return self.options.get('secret_coins', 0)

    @property
    def user_coins(self):
        """:class:`int`: Amount of User Coins user has."""
        return self.options.get('coins', 0)

    @property
    def lb_place(self):
        """:class:`int`: User's place in leaderboard. ``0`` if not set."""
        return self.options.get('lb_place', 0)

    def has_cp(self):
        """:class:`bool`: Indicates if a user has Creator Points."""
        return self.cp > 0

    def set_place(self, place: int = 0):
        """Set the ``self.lb_place`` to ``place`` argument."""
        self.options['lb_place'] = place

    async def update(self):
        """|coro|

        Update ``self``.
        """
        new = await self._client.fetch_user(self.account_id, stats=True)

        new.set_place(self.lb_place)

        self.options = new.options

class User(UserStats):
    """Class that represents a Geometry Dash User.
    This class is derived from :class:`.UserStats`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    def __repr__(self):
        info = {
            'account_id': self.account_id,
            'id': self.id,
            'name': repr(self.name),
            'role': self.role,
            'cp': self.cp
        }
        return make_repr(self, info)

    @property
    def role(self):
        """:class:`.StatusLevel`: A status level of the user."""
        return self.options.get('role', StatusLevel(0))

    @property
    def rank(self):
        """Union[:class:`int`, ``None``]: A global rank of the user.
        ``None`` if the user is not on the leaderboard.
        """
        return self.options.get('global_rank')

    @property
    def youtube(self):
        """:class:`str`: A youtube name of the user."""
        return self.options.get('youtube', {}).get('normal', '')

    @property
    def youtube_link(self):
        """:class:`str`: A link to the user's youtube channel."""
        return self.options.get('youtube', {}).get('link', '')

    @property
    def twitter(self):
        """:class:`str`: A twitter name of the user."""
        return self.options.get('twitter', {}).get('normal', '')

    @property
    def twitter_link(self):
        """:class:`str`: A link to the user's twitter page."""
        return self.options.get('twitter', {}).get('link', '')

    @property
    def twitch(self):
        """:class:`str`: A twitch name of the user."""
        return self.options.get('twitch', {}).get('normal', '')

    @property
    def twitch_link(self):
        """:class:`str`: A link to the user's twitch channel."""
        return self.options.get('twitch', {}).get('link', '')

    @property
    def msg_policy(self):
        """:class:`.MessagePolicyType`: A type indicating user's message inbox policy."""
        return self.options.get('messages', MessagePolicyType(0))

    @property
    def friend_req_policy(self):
        """:class:`.FriendRequestPolicyType`: A type indicating user's friend requests policy."""
        return self.options.get('friend_requests', FriendRequestPolicyType(0))

    @property
    def comments_policy(self):
        """:class:`.CommentPolicyType`: A type indicating user's comment history policy."""
        return self.options.get('comments', CommentPolicyType(0))

    @property
    def icon_set(self):
        """:class:`.IconSet`: An iconset of the user."""
        return self.options.get('icon_setup', IconSet())

    def is_mod(self, elder: str = None):
        """:class:`bool`: Indicates if a user is Geometry Dash (Elder) Moderator.
        For instance, *RobTop* is an Elder Moderator, that means:
        ``robtop.is_mod() -> True`` and ``robtop.is_mod('elder') -> True``.
        """
        if self.role is None:
            return False

        elif elder is None:
            return self.role.value >= 1

        elif elder == 'elder':
            return self.role.value == 2

        raise TypeError("is_mod(elder) expected elder=='elder', or None.")

    async def update(self):
        """|coro|

        Update the user's statistics and other parameters.
        """
        new = await self._client.get_user(self.account_id)
        self.options = new.options
