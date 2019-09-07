from .abstractuser import AbstractUser
from .session import _session
from .utils.converter import Converter
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
            'name': self.name,
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
        return self.options.get('stars')

    @property
    def demons(self):
        """:class:`int`: Amount of demons the user has beaten."""
        return self.options.get('demons')

    @property
    def cp(self):
        """:class:`int`: Amount of Creator Points the user has."""
        return self.options.get('cp')

    @property
    def diamonds(self):
        """:class:`int`: Amount of diamonds the user has."""
        return self.options.get('diamonds')

    @property
    def coins(self):
        """:class:`int`: Number of coins the user has."""
        return self.options.get('coins')

    @property
    def user_coins(self):
        """:class:`int`: Amount of User Coins user has."""
        return self.options.get('user_coins')

    @property
    def lb_place(self):
        """:class:`int`: User's place in leaderboard. ``-1`` if not set."""
        return self.options.get('lb_place', -1)

    def has_cp(self):
        """:class:`bool`: Indicates if a user has Creator Points."""
        return self.cp > 0

    async def update(self):
        """|coro|

        Update ``self``.
        """
        new = await self._client.fetch_user(self.account_id, stats=True)
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
            'name': self.name,
            'role': self.role,
            'cp': self.cp
        }
        return make_repr(self, info)

    @property
    def role(self):
        """:class:`.StatusLevel`: A status level of the user."""
        return self.options.get('role')

    @property
    def rank(self):
        """Union[:class:`int`, ``None``]: A global rank of the user.
        ``None`` if the user is not on the leaderboard.
        """
        return self.options.get('global_rank')

    @property
    def youtube(self):
        """Union[:class:`str`, ``None``]: A youtube name of the user."""
        return self.options.get('youtube')[0]

    @property
    def youtube_link(self):
        """Union[:class:`str`, ``None``]: A link to the user's youtube channel."""
        return self.options.get('youtube')[1]

    @property
    def twitter(self):
        """Union[:class:`str`, ``None``]: A twitter name of the user."""
        return self.options.get('twitter')[0]

    @property
    def twitter_link(self):
        """Union[:class:`str`, ``None``]: A link to the user's twitter page."""
        return self.options.get('twitter')[1]

    @property
    def twitch(self):
        """Union[:class:`str`, ``None``]: A twitch name of the user."""
        return self.options.get('twitch')[0]

    @property
    def twitch_link(self):
        """Union[:class:`str`, ``None``]: A link to the user's twitch channel."""
        return self.options.get('twitch')[1]

    @property
    def msg_policy(self):
        """:class:`.MessagePolicyType`: A type indicating user's message inbox policy."""
        return self.options.get('messages')

    @property
    def friend_req_policy(self):
        """:class:`.FriendRequestPolicyType`: A type indicating user's friend requests policy."""
        return self.options.get('friend_requests')

    @property
    def comments_policy(self):
        """:class:`.CommentPolicyType`: A type indicating user's comment history policy."""
        return self.options.get('comments')

    @property
    def icon_set(self):
        """:class:`.IconSet`: An iconset of the user."""
        return self.options.get('icon_setup')

    def is_mod(self, elder: str = None):
        """:class:`bool`: Indicates if a user is Geometry Dash (Elder) Moderator.
        For instance, *RobTop* is an Elder Moderator, that means:
        ``robtop.is_mod() -> True`` and ``robtop.is_mod('elder') -> True``.
        """
        if self.role is None:
            return False

        elif elder == None:
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
