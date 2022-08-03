from functools import wraps
from threading import RLock
from time import monotonic as clock
from typing import Optional, Type, TypeVar

from aiohttp.web import Request, Response
from attrs import define, field

from gd.server.constants import HTTP_TOO_MANY_REQUESTS, TOKEN
from gd.server.handler import Error, ErrorType
from gd.server.typing import Handler
from gd.typing import DecoratorIdentity, Nullary, StringDict, Unary

__all__ = (
    "CooldownWith",
    "Cooldown",
    "CooldownThreadsafe",
    "CooldownMapping",
    "cooldown",
    "cooldown_remote_and_token",
    "cooldown_remote",
    "cooldown_token",
)

RETRY_AFTER = "Retry-After"

Clock = Nullary[float]

CooldownWith = Unary[Request, str]

C = TypeVar("C", bound="Cooldown")


@define()
class Cooldown:
    rate: int = field()
    per: float = field()

    _clock: Clock = field(default=clock)

    _tokens: int = field()

    _last: float = field(default=0.0)
    _window: float = field(default=0.0)

    @_tokens.default
    def default_tokens(self) -> int:
        return self.rate

    @property
    def clock(self) -> Clock:
        return self._clock

    @property
    def tokens(self) -> int:
        return self._tokens

    @property
    def last(self) -> float:
        return self._last

    @property
    def window(self) -> float:
        return self._window

    def copy(self: C) -> C:
        return type(self)(self.rate, self.per, self.clock)

    def update_rate_limit(self, current: Optional[float] = None) -> Optional[float]:
        if not current:
            current = self.clock()

        self._last = current  # may be used externally

        if current > self.window + self.per:
            self._tokens = self.rate  # reset token state

        if self._tokens == self.rate:  # first iteration after reset
            self._window = current  # update window to current

        if not self._tokens:  # rate limited -> return retry_after
            return self.per - (current - self._window)

        self._tokens -= 1  # not rate limited -> decrement tokens

        # if we got rate limited due to this token change,
        # update the window to point to our current time frame
        if not self._tokens:
            self._window = current

        return None  # not rate limited


@define()
class CooldownThreadsafe(Cooldown):
    _lock: RLock = field(factory=RLock)

    def update_rate_limit(self, current: Optional[float] = None) -> Optional[float]:
        with self._lock:
            return super().update_rate_limit(current)


CM = TypeVar("CM", bound="CooldownMapping")


@define()
class CooldownMapping:
    cooldown: Cooldown = field()
    cooldown_with: CooldownWith = field()

    cache: StringDict[Cooldown] = field(factory=dict, init=False)

    def copy(self: CM) -> CM:
        copy = type(self)(self.cooldown, self.cooldown_with)
        copy.cache.update(self.cache)

        return copy

    def clear_cache(self) -> None:
        self.cache.clear()

    def clear_unused_cache(self, current: Optional[float] = None) -> None:
        if not current:
            current = self.cooldown.clock()

        self.cache = {
            key: value for key, value in self.cache.items() if current < value.last + value.per
        }

    def get_bucket(self, request: Request) -> Cooldown:
        cooldown_with = self.cooldown_with(request)

        if cooldown_with in self.cache:
            bucket = self.cache[cooldown_with]

        else:
            bucket = self.cooldown.copy()
            self.cache[cooldown_with] = bucket

        return bucket

    def update_rate_limit(
        self, request: Request, current: Optional[float] = None
    ) -> Optional[float]:
        self.clear_unused_cache(current)

        bucket = self.get_bucket(request)

        return bucket.update_rate_limit(current)

    @classmethod
    def from_cooldown(
        cls: Type[CM],
        rate: int,
        per: float,
        by: CooldownWith,
        cooldown_type: Type[Cooldown] = Cooldown,
    ) -> CM:
        return cls(cooldown_type(rate, per), by)


RATE_LIMITED = "rate limited; retry after {} seconds"


def create_cooldown_error(retry_after: float) -> Error:
    return Error(
        status=HTTP_TOO_MANY_REQUESTS,
        type=ErrorType.RATE_LIMITED,
        message=RATE_LIMITED.format(retry_after),
        headers={RETRY_AFTER: str(retry_after)},
    )


def cooldown_remote(request: Request) -> str:
    return request.remote  # type: ignore


def cooldown_token(request: Request) -> str:
    return request[TOKEN]


AT = "{}@{}"


def cooldown_remote_and_token(request: Request) -> str:
    return AT.format(cooldown_token(request), cooldown_remote(request))


def cooldown(
    rate: int,
    per: float,
    by: CooldownWith = cooldown_token,
    cooldown_type: Type[Cooldown] = Cooldown,
    cooldown_mapping_type: Type[CooldownMapping] = CooldownMapping,
    retry_after_precision: int = 2,
) -> DecoratorIdentity[Handler]:
    def wrap(handler: Handler) -> Handler:
        mapping = cooldown_mapping_type.from_cooldown(rate, per, by, cooldown_type=cooldown_type)

        @wraps(handler)
        async def retry_after_handler(request: Request) -> Response:
            retry_after = mapping.update_rate_limit(request)

            if retry_after is None:
                return await handler(request)

            return create_cooldown_error(round(retry_after, retry_after_precision)).into_response()

        return retry_after_handler

    return wrap
