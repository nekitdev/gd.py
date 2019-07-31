import asyncio
import itertools

from typing import Sequence, Union

from . import classconverter
from . import client
from .errors import MissingAccess, NothingFound

from .utils.http_request import http
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.mapper import mapper_util
from .utils.gdpaginator import paginate as pagin
from .abstractentity import AbstractEntity
from .utils.context import ctx
from .utils.wrap_tools import _make_repr, check

#TO_DO: add __repr__ func

class User(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options

    @property
    def name(self):
        return self.options.get('name')

    @property
    def account_id(self):
        return self.options.get('account_id')

    @property
    def stars(self):
        return self.options.get('stars')

    @property
    def demons(self):
        return self.options.get('demons')

    @property
    def cp(self):
        return self.options.get('cp')

    @property
    def diamonds(self):
        return self.options.get('diamonds')

    @property
    def role(self):
        return self.options.get('role')

    @property
    def rank(self):
        return self.options.get('global_rank')

    @property
    def youtube(self):
        return self.options.get('youtube')

    @property
    def twitter(self):
        return self.options.get('twitter')[0]

    @property
    def twitter_link(self):
        return self.options.get('twitter')[1]

    @property
    def twitch(self):
        return self.options.get('twitch')[0]

    @property
    def twitch_link(self):
        return self.options.get('twitch')[1]

    @property
    def msg_policy(self):
        return self.options.get('messages')

    @property
    def friend_req_policy(self):
        return self.options.get('friend_requests')

    @property
    def comments_policy(self):
        return self.options.get('comments')

    @property
    def icon_set(self):
        return self.options.get('icon_setup')

    @property
    def _dict_for_parse(self):
        return {
            k: getattr(self, k) for k in ('name', 'id', 'account_id')
        }
    

    def is_mod(self, elder: str = None):
        if elder == None:
            return self.role.level >= 1
        if elder == 'elder':
            return self.role.level == 2
        raise TypeError("is_mod(elder) expected elder=='elder', or None.")
    
    def has_cp(self):
        return self.cp > 0

    async def get_page_comments(self, page: int = 0):
        """|coro|

        Gets user's profile comments on a specific page.

        This is equivalent to:
            await self.retrieve_page_comments('profile', page)
        """
        return await self.retrieve_page_comments('profile', page)

    async def get_page_comment_history(self, page: int = 0):
        """|coro|

        Gets user's level (history) comments on a specific page.

        This is equivalent to:
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
        assert isinstance(page, int) and page >= 0
        assert typeof in ("profile", "level")

        is_level = (typeof == "level")

        typeid = 0 if is_level else 1
        definer = "userid" if is_level else "accountid"
        selfid = str(self.id if is_level else self.account_id)
        route = Route.GET_COMMENT_HISTORY if is_level else Route.GET_COMMENTS

        def func(elem):
            if is_level:
                return elem.split(':')[0].split('~')
            return elem.split('~')

        param_obj = Params().create_new().put_definer(definer, selfid).put_page(page).put_total(0)
        if is_level:
            param_obj.put_mode(0)
        params = param_obj.finish()

        resp = await http.fetch(route, params, splitter='#')
        thing = resp[0]

        if not len(thing):
            if raise_errors:
                raise NothingFound('gd.Comment')
            return list()

        to_map = mapper_util.normalize(thing).split('|')

        res = []
        for elem in to_map:
            prepared = mapper_util.map(
                func(elem) + ['101', str(typeid), '102', str(page)]
            )
            res.append(
                classconverter.ClassConverter.comment_convert(
                    prepared, self._dict_for_parse
                )
            )

        return res

    async def retrieve_comments(
        self, typeof: str = 'profile', pages: Sequence[int] = [],
        *, sort_by_page: bool = True, timeout: Union[int, float] = 5.0
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
        assert typeof in ('profile', 'level')
        assert len(pages) <= 100

        real_pages = filter(lambda n: isinstance(n, int), pages)
        to_run = [
            self.retrieve_page_comments(typeof, page, raise_errors=False) for page in real_pages
        ]

        finished, _ = await asyncio.wait(to_run, timeout=30.0)

        filtered = [
            fut.result() for fut in finished if fut.result()
        ]

        if sort_by_page:
            # sort the lists according to the page of the first comment in each list.
            filtered.sort(key=lambda s: s[0].page)
        return [*itertools.chain.from_iterable(filtered)]

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
        params = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_message(subject, body).put_recipient(str(self.account_id)).put_password(ctx.encodedpass).finish()
        resp = await http.request(Route.SEND_PRIVATE_MESSAGE, params)
        if resp != 1:
            raise MissingAccess(f"Failed to send a message to a user: {self!r}.")
        
    async def update(self):
        """|coro|

        Update the user's statistics and other parameters.
        """
        new = await client.Client().get_user(self.account_id)
        self.options = new.options
