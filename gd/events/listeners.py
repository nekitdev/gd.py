from __future__ import annotations

from abc import abstractmethod
from traceback import print_exc as print_current_exception
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Hashable,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
)

from attrs import define, field
from typing_extensions import Protocol

from gd.async_utils import awaiting, get_running_loop
from gd.comments import Comment
from gd.constants import DEFAULT_PAGES_COUNT, DEFAULT_RECONNECT
from gd.enums import SearchStrategy
from gd.filters import Filters
from gd.friend_request import FriendRequest
from gd.level import Level
from gd.message import Message
from gd.tasks import Loop
from gd.user import User

__all__ = (
    "DEFAULT_DELAY",
    "Listener",
    "DailyLevelListener",
    "WeeklyLevelListener",
    "LevelListener",
    "RateListener",
    "MessageListener",
    "FriendRequestListener",
    # "LevelCommentListener",
    # "DailyCommentListener",
    # "WeeklyCommentListener",
    "UserCommentListener",
    "UserLevelListener",
)

if TYPE_CHECKING:
    from gd.client import Client  # noqa

LISTENER_ALREADY_STARTED = "listener has already started"


DEFAULT_DELAY = 10.0


class ListenerProtocol(Protocol):
    delay: float
    count: Optional[int]
    reconnect: bool
    _started: bool

    @abstractmethod
    async def step(self) -> None:
        ...

    async def on_error(self, error: Exception) -> None:
        print_current_exception()

    async def schedule(self, awaitable: Awaitable[Any]) -> None:
        get_running_loop().create_task(awaiting(awaitable))

    async def main(self) -> None:
        try:
            await self.step()

        except Exception as error:
            await self.on_error(error)

    def start(self) -> None:
        if self._started:
            raise RuntimeError(LISTENER_ALREADY_STARTED)

        loop = Loop(
            function=self.main, delay=self.delay, count=self.count, reconnect=self.reconnect
        )

        loop.start()

        self._started = True


@define()
class Listener(ListenerProtocol):
    client: Client = field()
    delay: float = field(default=DEFAULT_DELAY)
    count: Optional[int] = field(default=None)
    reconnect: bool = field(default=DEFAULT_RECONNECT)

    _started: bool = field(default=False, init=False)

    async def step(self) -> None:
        pass


@define()
class DailyLevelListener(Listener):
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
class WeeklyLevelListener(Listener):
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


@define()
class RateListener(LevelListener):
    filters: Filters = field(default=Filters(SearchStrategy.AWARDED))

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
            await self.schedule(client.dispatch_friend_request(message))


DEFAULT_UPDATE = True
# DEFAULT_COUNT = 100


# @define()
# class LevelCommentListener(Listener):
#     level_id: int = field(default=0)

#     count: int = field(default=DEFAULT_COUNT)

#     update: bool = field(default=DEFAULT_UPDATE)

#     level: Level = field(init=False)
#     level_comments_cache: List[LevelComment] = field(factory=list, init=False)

#     async def get_level(self) -> Level:
#         return await self.client.get_level(self.level_id)

#     async def dispatch_level_comment(self, level: Level, comment: LevelComment) -> None:
#         await self.client.dispatch_level_comment(level, comment)

#     async def step(self) -> None:
#         level = self.level

#         if level is None:
#             self.level = level = await self.client.get_level(self.level_id)

#         level_comments = await level.get_comments(count=self.count)

#         if not level_comments:
#             return

#         level_comments_cache = self.level_comments_cache

#         if not level_comments_cache:
#             self.level_comments_cache = level_comments

#             return

#         difference = differ(level_comments_cache, level_comments)

#         self.level_comments_cache = level_comments

#         if difference and self.update:
#             await level.update()

#         for comment in difference:
#             await self.schedule(self.dispatch_level_comment(level, comment))


# @define()
# class DailyCommentListener(Listener):
#     level_id: int = TimelyID.DAILY.value

#     async def get_level(self) -> Level:
#         return await self.client.get_daily()

#     async def dispatch_level_comment(self, level: Level, comment: LevelComment) -> None:
#         await self.client.dispatch_daily_comment(level, comment)


# @define()
# class WeeklyCommentListener(Listener):
#     level_id: int = TimelyID.WEEKLY.value

#     async def get_level(self) -> Level:
#         return await self.client.get_weekly()

#     async def dispatch_level_comment(self, level: Level, comment: LevelComment) -> None:
#         await self.client.dispatch_weekly_comment(level, comment)


QUERY_EXPECTED = "expected either `account_id`, `id` or `name` query"

DEFAULT_LEVEL = False


@define()
class UserCommentListener(Listener):
    account_id: Optional[int] = field(default=None)
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)

    level: bool = field(default=DEFAULT_LEVEL)

    pages_count: int = field(default=DEFAULT_PAGES_COUNT)

    user: Optional[User] = field(default=None, init=False)

    user_comments_cache: List[Comment] = field(factory=list, init=False)

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

    async def step(self) -> None:
        user = self.user

        if user is None:
            self.user = user = await self.find_user()

        if self.level:
            user_comments = await user.get_level_comments(pages=range(self.pages_count))

        else:
            user_comments = await user.get_comments(pages=range(self.pages_count))

        if not user_comments:
            return

        user_comments_cache = self.user_comments_cache

        if not user_comments_cache:
            self.user_comments_cache = user_comments

            return

        difference = differ(user_comments_cache, user_comments)

        client = self.client

        for comment in difference:
            await self.schedule(client.dispatch_user_comment(user, comment))


@define()
class UserLevelListener(Listener):
    account_id: Optional[int] = field(default=None)
    id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)

    update: bool = field(default=DEFAULT_UPDATE)

    pages_count: int = field(default=DEFAULT_PAGES_COUNT)

    user: Optional[User] = field(default=None, init=False)

    user_levels_cache: List[Level] = field(factory=list, init=False)

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

        client = self.client

        for level in difference:
            await self.schedule(client.dispatch_user_level(user, level))


Q = TypeVar("Q", bound=Hashable)


def differ(before: Iterable[Q], after: Iterable[Q]) -> Iterator[Q]:
    before_set = set(before)

    for item in after:
        if item in before_set:
            break

        yield item
