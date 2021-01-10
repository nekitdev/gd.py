import time
from functools import wraps
from threading import Lock

from gd.server.common import web
from gd.server.handler import Error, ErrorType
from gd.server.typing import Handler
from gd.text_utils import make_repr
from gd.typing import Callable, Dict, Optional, Type, TypeVar

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

Clock = Callable[[], float]

CooldownWith = Callable[[web.Request], str]

CooldownT = TypeVar("CooldownT", bound="Cooldown")
CooldownMappingT = TypeVar("CooldownMappingT", bound="CooldownMapping")


class Cooldown:
    def __init__(self, rate: int, per: float, clock: Clock = time.monotonic) -> None:
        self.rate = int(rate)
        self.per = float(per)

        self._clock = clock

        self._tokens = self.rate

        self._last = 0.0

        self._window = 0.0

    def __repr__(self) -> str:
        info = {
            "rate": self.rate,
            "per": self.per,
            "tokens": self.tokens,
            "window": self.window,
            "last": self.last,
        }

        return make_repr(self, info)

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

    def copy(self: CooldownT) -> CooldownT:
        return self.__class__(self.rate, self.per, self.clock)

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


class CooldownThreadsafe(Cooldown):
    def __init__(self, rate: int, per: float, clock: Clock = time.monotonic) -> None:
        super().__init__(rate, per, clock)

        self._lock = Lock()

    def update_rate_limit(self, current: Optional[float] = None) -> Optional[float]:
        with self._lock:
            return super().update_rate_limit(current)


class CooldownMapping:
    def __init__(self, cooldown: Cooldown, cooldown_with: CooldownWith) -> None:
        self.cache: Dict[str, Cooldown] = {}

        self.cooldown = cooldown
        self.cooldown_with = cooldown_with

    def copy(self: CooldownMappingT) -> CooldownMappingT:
        self_copy = self.__class__(self.cooldown, self.cooldown_with)
        self_copy.cache = self.cache.copy()

        return self_copy

    def clear_unused_cache(self, current: Optional[float] = None) -> None:
        if not current:
            current = time.monotonic()

        self.cache = {
            key: value for key, value in self.cache.items() if current < value.last + value.per
        }

    def get_bucket(self, request: web.Request, current: Optional[float] = None) -> Cooldown:
        self.clear_unused_cache()

        cooldown_with = self.cooldown_with(request)

        if cooldown_with in self.cache:
            bucket = self.cache[cooldown_with]

        else:
            bucket = self.cooldown.copy()
            self.cache[cooldown_with] = bucket

        return bucket

    def update_rate_limit(
        self, request: web.Request, current: Optional[float] = None
    ) -> Optional[float]:
        bucket = self.get_bucket(request, current)

        return bucket.update_rate_limit(current)

    @classmethod
    def from_cooldown(
        mapping_cls: Type[CooldownMappingT],
        rate: int,
        per: float,
        by: CooldownWith,
        cls: Type[Cooldown] = Cooldown,
    ) -> CooldownMappingT:
        return mapping_cls(cls(rate, per), by)


def create_cooldown_error(retry_after: float) -> Error:
    return Error(
        429,
        ErrorType.RATE_LIMITED,
        message=f"Rate limited. Retry after {retry_after} seconds.",
        retry_after=retry_after,
        headers={RETRY_AFTER: f"{retry_after}"},
    )


def cooldown_remote(request: web.Request) -> str:
    return f"{request.remote}"


def cooldown_token(request: web.Request) -> str:
    return f"{request.token}"  # type: ignore


def cooldown_remote_and_token(request: web.Request) -> str:
    return f"{request.remote}_{request.token}"  # type: ignore


def cooldown(
    rate: int,
    per: float,
    by: CooldownWith,
    cls: Type[Cooldown] = Cooldown,
    mapping_cls: Type[CooldownMapping] = CooldownMapping,
    retry_after_precision: int = 2,
) -> Callable[[Handler], Handler]:
    def wrapper(handler: Handler) -> Handler:
        mapping = mapping_cls.from_cooldown(rate, per, by, cls=cls)

        @wraps(handler)
        async def actual_handler(request: web.Request) -> web.StreamResponse:
            retry_after = mapping.update_rate_limit(request)

            if retry_after is None:
                return await handler(request)

            else:
                return create_cooldown_error(
                    round(retry_after, retry_after_precision)
                ).into_response()

        return actual_handler

    return wrapper
