import asyncio
import itertools

from typing import Sequence, Union

from .errors import MissingAccess, NothingFound

from .abstractentity import AbstractEntity
from .session import GDSession
from .utils.context import ctx
from .utils.wrap_tools import _make_repr, check

#TO_DO: add __repr__ func

_session = GDSession()

class User(AbstractEntity):
    """Class that represents a Geometry Dash User."""
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    def __repr__(self):
        info = {
            'account_id': self.account_id,
            'name': self.name,
            'role': self.role,
            'cp': self.cp
        }
        return _make_repr(self, info)

    @property
    def name(self):
        """:class:`str`: A name of the user."""
        return self.options.get('name')

    @property
    def account_id(self):
        """:class:`int`: An account ID of the user."""
        return self.options.get('account_id')

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
        """:class:`.MessagePolicyType` A type indicating user's message inbox policy."""
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
        """:class:`.IconSet` An iconset of the user."""
        return self.options.get('icon_setup')

    @property
    def _dict_for_parse(self):
        return {
            k: getattr(self, k) for k in ('name', 'id', 'account_id')
        }
    

    def is_mod(self, elder: str = None):
        """:class:`bool`: Indicates if a user is Geometry Dash (Elder) Moderator.
        For instance, *RobTop* is an Elder Moderator, that means: 
        ``robtop.is_mod() -> True`` and ``robtop.is_mod('elder') -> True``.
        """
        if elder == None:
            return self.role.level >= 1
        if elder == 'elder':
            return self.role.level == 2
        raise TypeError("is_mod(elder) expected elder=='elder', or None.")
    
    def has_cp(self):
        """:class:`bool`: Indicates if a user has Creator Points."""
        return self.cp > 0

    async def get_page_comments(self, page: int = 0):
        """|coro|

        Gets user's profile comments on a specific page.

        This is equivalent to:

        .. code-block:: python3

            await self.retrieve_page_comments('profile', page)
        """
        return await self.retrieve_page_comments('profile', page)

    async def get_page_comment_history(self, page: int = 0):
        """|coro|

        Gets user's level (history) comments on a specific page.

        This is equivalent to:

        .. code-block:: python3

            await self.retrieve_page_comments('level', page)
        """
        return await self.retrieve_page_comments('level', page)

    async def get_comments(
        self, pages: Sequence[int] = [],
        *, sort_by_page: bool = True,
        timeout: Union[int, float] = 5.0
    ):
        """|coro|

        Gets user's profile comments on specific pages.

        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments(
                'profile', pages, sort_by_page=sort_by_page, timeout=timeout
            )
        """
        return await self.retrieve_comments(
            'profile', pages, sort_by_page=sort_by_page, timeout=timeout
        )

    async def get_comment_history(
        self, pages: Sequence[int] = [],
        *, sort_by_page: bool = True,
        timeout: Union[int, float] = 5.0
    ):
        """|coro|

        Gets user's level (history) comments on specific pages.
        
        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments(
                'level', pages, sort_by_page=sort_by_page, timeout=timeout
            )
        """
        return await self.retrieve_comments(
            'level', pages, sort_by_page=sort_by_page, timeout=timeout
        )

    async def retrieve_page_comments(
        self, typeof: str = 'profile', page: int = 0, *, raise_errors: bool = True
    ):
        """|coro|

        Utilizes getting comments. This is used in two other methods,
        :meth:`.User.get_page_comments` and :meth:`.User.get_page_comment_history`.

        Parameters
        ----------
        typeof: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        page: :class:`int`
            Page to look comments at.

        raise_errors: :class:`bool`
            Indicates whether :exc:`.NothingFound` should be raised.
            Should be set to false when getting several pages of comments,
            like in :meth:`.User.retrieve_comments`.

        Returns
        -------
        List[:class:`.Comment`]
            List of all comments retrieved, if comments were found.

        Raises
        ------
        :exc:`.NothingFound`
            No comments were found.        
        """
        return await _session.retrieve_page_comments(
            typeof=typeof, user=self, page=page, raise_errors=raise_errors
        )

    async def retrieve_comments(
        self, typeof: str = 'profile', pages: Sequence[int] = [],
        *, sort_by_page: bool = True, timeout: Union[int, float] = 10.0
    ):
        """|coro|

        Utilizes getting comments on specified pages.

        Parameters
        ----------
        typeof: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        sort_by_page: :class:`bool`
            Indicates whether returned comments should be sorted by page.

        timeout: Union[:class:`int`, :class:`float`]
            Timeout to stop requesting after it occurs.
            Used to prevent insanely long responses.

        Returns
        -------
        List[:class:`.Comment`]
            List of comments found. Can be an empty list.
        """
        return await _session.retrieve_comments(
            typeof=typeof, user=self, pages=pages, sort_by_page=sort_by_page, timeout=timeout
        )

    @check.is_logged(ctx)
    async def update_profile(
        self, *, msg: int = None, friend_req: int = None, comments: int = None,
        youtube: str = None, twitter: str = None, twitch: str = None
    ):
        things = ('msg', 'friend_req', 'comments', 'youtube', 'twitter', 'twitch')

        args = []
        # check, if arg is None, set the existing one
        for arg in things:
            tmp = locals().get(arg)
            if arg in things[:3]:
                s = getattr(self, arg + '_policy').level
            else:
                s = str(getattr(self, arg)).replace('None', '')

            args.append(tmp if tmp is not None else s)

        await _session.update_profile(self, *args)

    @check.is_logged(ctx)
    async def send(self, subject: str, body: str):
        """|coro|

        Send the message to ``self``. Requires logged client.

        Parameters
        ----------
        subject: :class:`str`
            The subject of the message.

        body: :class:`str`
            The body of the message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a message.
        """
        await _session.send_message(target=self, subject=subject, body=body)

    async def update(self):
        """|coro|

        Update the user's statistics and other parameters.
        """
        new = await _session.get_user(self.account_id)
        self.options = new.options
