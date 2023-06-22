from __future__ import annotations

from abc import abstractmethod as required
from asyncio import get_running_loop
from traceback import print_exception as print_error
from typing import TYPE_CHECKING, Any, Awaitable, Hashable, Iterable, List, Optional, TypeVar

from attrs import define, field
from funcs.functions import awaiting
from iters.iters import Iter, iter
from typing_aliases import NormalError, Nullary, Predicate
from typing_extensions import Protocol

from gd.comments import LevelComment, UserComment
from gd.constants import (
    DEFAULT_COUNT,
    DEFAULT_DELAY,
    DEFAULT_ID,
    DEFAULT_PAGES_COUNT,
    DEFAULT_RECONNECT,
    DEFAULT_UPDATE,
)
from gd.enums import SearchStrategy, TimelyID
from gd.filters import Filters
from gd.friend_request import FriendRequest
from gd.level import Level
from gd.message import Message
from gd.tasks import Loop
from gd.users import User

__all__ = (
    "Listener",
    "DailyListener",
    "WeeklyListener",
    "LevelListener",
    "RateListener",
    "MessageListener",
    "FriendRequestListener",
    "LevelCommentListener",
    "DailyCommentListener",
    "WeeklyCommentListener",
    "UserCommentListener",
    "UserLevelCommentListener",
    "UserLevelListener",
)

if TYPE_CHECKING:
    from gd.client import Client


Q = TypeVar("Q", bound=Hashable)


def not_in_before_set(before: Iterable[Q]) -> Predicate[Q]:
    before_set = set(before)

    def predicate(item: Q) -> bool:
        return item not in before_set

    return predicate


def differ_iterator(before: Iterable[Q], after: Iterable[Q]) -> Iter[Q]:
    return iter(after).take_while(not_in_before_set(before))


def differ(before: Iterable[Q], after: Iterable[Q]) -> List[Q]:
    return differ_iterator(before, after).list()


LISTENER_ALREADY_RUNNING = "listener is already running"


class ListenerProtocol(Protocol):
    delay: float
    reconnect: bool
    _running: bool
    _loop: Optional[Loop[[]]]

    @required
    async def step(self) -> None:
        ...

    async def on_error(self, error: NormalError) -> None:
        print_error(error)

    async def schedule(self, awaitable: Awaitable[Any]) -> None:
        get_running_loop().create_task(awaiting(awaitable))

    async def main(self) -> None:
        try:
            await self.step()

        except NormalError as error:
            await self.on_error(error)

    def start(self) -> None:
        if self._running:  # type: ignore
            raise RuntimeError(LISTENER_ALREADY_RUNNING)

        loop = Loop(function=self.main, delay=self.delay, reconnect=self.reconnect)

        self._loop = loop

        loop.start()

        self._running = True


@define()
class Listener(ListenerProtocol):
    client: Client = field()

    delay: float = field(default=DEFAULT_DELAY)
    reconnect: bool = field(default=DEFAULT_RECONNECT)

    _running: bool = field(default=False, init=False, repr=False)

    _loop: Optional[Loop[[]]] = field(default=None, init=False, repr=False)

    async def step(self) -> None:
        pass


@define()
class DailyListener(Listener):
    daily_cache: Optional[Level] = field(default=None, init=False)

    async def step(self) -> None:
        client = self.client

        daily = await client.get_daily()

        daily_cache = self.daily_cache

        if daily_cache is None:
            self.daily_cache = daily

            return

        self.daily_cache = daily

        if daily.id != daily_cache.id:
            await self.schedule(client.dispatch_daily(daily))


@define()
class WeeklyListener(Listener):
    weekly_cache: Optional[Level] = field(default=None, init=False)

    async def step(self) -> None:
        client = self.client

        weekly = await client.get_weekly()

        weekly_cache = self.weekly_cache

        if weekly_cache is None:
            self.weekly_cache = weekly

            return

        self.weekly_cache = weekly

        if weekly.id != weekly_cache.id:
            await self.schedule(client.dispatch_weekly(weekly))


@define()
class LevelListener(Listener):
    pages_count: int = field(default=DEFAULT_PAGES_COUNT)
    filters: Filters = field(factory=Filters)

    levels_cache: List[Level] = field(factory=list, init=False)

    async def dispatch_level(self, level: Level) -> None:
        await self.client.dispatch_level(level)

    async def step(self) -> None:
        levels = await self.client.search_levels(
            filters=self.filters, pages=range(self.pages_count)
        ).list()

        if not levels:  # abort
            return

        levels_cache = self.levels_cache

        if not levels_cache:
            self.levels_cache = levels

            return

        difference = differ(levels_cache, levels)

        self.levels_cache = levels

        for level in difference:
            await self.schedule(self.dispatch_level(level))


def filters_factory(strategy: SearchStrategy) -> Nullary[Filters]:
    def factory() -> Filters:
        return Filters(strategy)

    return factory


@define()
class RateListener(LevelListener):
    filters: Filters = field(factory=filters_factory(SearchStrategy.RATED))

    async def dispatch_level(self, level: Level) -> None:
        await self.client.dispatch_rate(level)


DEFAULT_READ = True


@define()
class MessageListener(Listener):
    pages_count: int = field(default=DEFAULT_PAGES_COUNT)

    messages_cache: List[Message] = field(factory=list, init=False)

    async def step(self) -> None:
        client = self.client

        messages = await client.get_messages(pages=range(self.pages_count))

        if not messages:
            return

        messages_cache = self.messages_cache

        if not messages_cache:
            self.messages_cache = messages

            return

        difference = differ(messages_cache, messages)

        self.messages_cache = messages

        for message in difference:
            await self.schedule(client.dispatch_message(message))


@define()
class FriendRequestListener(Listener):
    pages_count: int = field(default=DEFAULT_PAGES_COUNT)

    friend_requests_cache: List[FriendRequest] = field(factory=list, init=False)

    async def step(self) -> None:
        client = self.client

        friend_requests = await client.get_friend_requests(pages=range(self.pages_count))

        if not friend_requests:
            return

        friend_requests_cache = self.friend_requests_cache

        if not friend_requests_cache:
            self.friend_requests_cache = friend_requests

            return

        difference = differ(friend_requests_cache, friend_requests)

        self.friend_requests_cache = friend_requests

        for friend_request in difference:
            await self.schedule(client.dispatch_friend_request(friend_request))


@define()
class LevelCommentListener(Listener):
    level_id: int = field(default=DEFAULT_ID)

    pages_count: int = field(default=DEFAULT_PAGES_COUNT)
    count: int = field(default=DEFAULT_COUNT)

    update: bool = field(default=DEFAULT_UPDATE)

    level: Optional[Level] = field(default=None, init=False)
    level_comments_cache: List[LevelComment] = field(factory=list, init=False)

    async def get_level(self) -> Level:
        return await self.client.get_level(self.level_id)

    async def dispatch_level_comment(self, level: Level, comment: LevelComment) -> None:
        await self.client.dispatch_level_comment(level, comment)

    async def step(self) -> None:
        level = self.level

        if level is None:
            self.level = level = await self.client.get_level(self.level_id)

        level_comments = await level.get_comments(count=self.count, pages=range(self.pages_count))

        if not level_comments:
            return

        level_comments_cache = self.level_comments_cache

        if not level_comments_cache:
            self.level_comments_cache = level_comments

            return

        difference = differ(level_comments_cache, level_comments)

        self.level_comments_cache = level_comments

        if difference and self.update:
            await level.update()

        for comment in difference:
            await self.schedule(self.dispatch_level_comment(level, comment))


@define()
class DailyCommentListener(LevelCommentListener):
    level_id: int = TimelyID.DAILY.value

    async def get_level(self) -> Level:
        return await self.client.get_daily()

    async def dispatch_level_comment(self, level: Level, comment: LevelComment) -> None:
        await self.client.dispatch_daily_comment(level, comment)


@define()
class WeeklyCommentListener(LevelCommentListener):
    level_id: int = TimelyID.WEEKLY.value

    async def get_level(self) -> Level:
        return await self.client.get_weekly()

    async def dispatch_level_comment(self, level: Level, comment: LevelComment) -> None:
        await self.client.dispatch_weekly_comment(level, comment)


QUERY_EXPECTED = "expected either `account_id`, `id` or `name` query"


@define()
class UserBasedListener(Listener):
    account_id: Optional[int] = None
    id: Optional[int] = None
    name: Optional[str] = None

    async def find_user(self) -> User:
        client = self.client

        account_id = self.account_id

        if account_id is not None:
            user = await client.get_user(account_id)

        else:
            id = self.id

            if id is not None:
                user = await client.search_user(id)

            else:
                name = self.name

                if name is not None:
                    user = await client.search_user(name)

                else:
                    raise ValueError(QUERY_EXPECTED)

        return user


@define()
class UserCommentListener(UserBasedListener):
    pages_count: int = field(default=DEFAULT_PAGES_COUNT)

    update: bool = DEFAULT_UPDATE

    user: Optional[User] = field(default=None, init=False)

    user_comments_cache: List[UserComment] = field(factory=list, init=False)

    async def step(self) -> None:
        user = self.user

        if user is None:
            self.user = user = await self.find_user()

        user_comments = await user.get_comments(pages=range(self.pages_count))

        if not user_comments:
            return

        user_comments_cache = self.user_comments_cache

        if not user_comments_cache:
            self.user_comments_cache = user_comments

            return

        difference = differ(user_comments_cache, user_comments)

        self.user_comments_cache = user_comments

        if difference and self.update:
            await user.update()

        client = self.client

        for comment in difference:
            await self.schedule(client.dispatch_user_comment(user, comment))


@define()
class UserLevelCommentListener(UserBasedListener):
    pages_count: int = field(default=DEFAULT_PAGES_COUNT)

    update: bool = DEFAULT_UPDATE

    user: Optional[User] = field(default=None, init=False)

    user_level_comments_cache: List[LevelComment] = field(factory=list, init=False)

    async def step(self) -> None:
        user = self.user

        if user is None:
            self.user = user = await self.find_user()

        user_level_comments = await user.get_level_comments(pages=range(self.pages_count))

        if not user_level_comments:
            return

        user_level_comments_cache = self.user_level_comments_cache

        if not user_level_comments_cache:
            self.user_level_comments_cache = user_level_comments

            return

        difference = differ(user_level_comments_cache, user_level_comments)

        self.user_level_comments_cache = user_level_comments

        if difference and self.update:
            await user.update()

        client = self.client

        for comment in difference:
            await self.schedule(client.dispatch_user_level_comment(user, comment))


@define()
class UserLevelListener(UserBasedListener):
    pages_count: int = field(default=DEFAULT_PAGES_COUNT)

    update: bool = field(default=DEFAULT_UPDATE)

    user: Optional[User] = field(default=None, init=False)

    user_levels_cache: List[Level] = field(factory=list, init=False)

    async def step(self) -> None:
        user = self.user

        if user is None:
            self.user = user = await self.find_user()

        user_levels = await user.get_levels(pages=range(self.pages_count))

        if not user_levels:
            return

        user_levels_cache = self.user_levels_cache

        if not user_levels_cache:
            self.user_levels_cache = user_levels

            return

        difference = differ(user_levels_cache, user_levels)

        self.user_levels_cache = user_levels

        if difference and self.update:
            await user.update()

        client = self.client

        for level in difference:
            await self.schedule(client.dispatch_user_level(user, level))
