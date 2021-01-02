import time
from functools import wraps

from gd.server.common import web
from gd.server.handler import Error, ErrorType
from gd.server.typing import Handler
from gd.typing import Callable, Dict, Optional, Type, TypeVar

__all__ = (
    "ConstructKey",
    "Cooldown",
    "CooldownMapping",
    "cooldown",
    "cooldown_remote_and_token",
    "cooldown_remote",
    "cooldown_token",
)

RETRY_AFTER = "Retry-After"

ConstructKey = Callable[[web.Request], str]

CooldownT = TypeVar("CooldownT", bound="Cooldown")
CooldownMappingT = TypeVar("CooldownMappingT", bound="CooldownMapping")


class Cooldown:
    def __init__(self, rate: int, per: float) -> None:
        self.rate = int(rate)
        self.tokens = self.rate

        self.per = float(per)
        self.last = 0.0

        self.window = 0.0

    def copy(self: CooldownT) -> CooldownT:
        return self.__class__(self.rate, self.per)

    def update_tokens(self, current: Optional[float] = None) -> None:
        if not current:
            current = time.monotonic()

        if current > self.window + self.per:
            self.tokens = self.rate  # reset token state

    def update_rate_limit(self, current: Optional[float] = None) -> Optional[float]:
        if not current:
            current = time.monotonic()

        self.last = current  # may be used externally

        self.update_tokens()

        if self.tokens == self.rate:  # first iteration after reset
            self.window = current  # update window to current

        if not self.tokens:  # rate limited -> return retry_after
            return self.per - (current - self.window)

        self.tokens -= 1  # not rate limited -> decrement tokens

        # if we got rate limited due to this token change,
        # update the window to point to our current time frame
        if not self.tokens:
            self.window = current

        return None  # not rate limited


class CooldownMapping:
    def __init__(self, original: Cooldown, construct_key: ConstructKey) -> None:
        self.cache: Dict[str, Cooldown] = {}

        self.original = original
        self.construct_key = construct_key

    def copy(self: CooldownMappingT) -> CooldownMappingT:
        self_copy = self.__class__(self.original, self.construct_key)
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

        key = self.construct_key(request)

        if key in self.cache:
            bucket = self.cache[key]

        else:
            bucket = self.original.copy()
            self.cache[key] = bucket

        return bucket

    def update_rate_limit(
        self, request: web.Request, current: Optional[float] = None
    ) -> Optional[float]:
        bucket = self.get_bucket(request, current)

        return bucket.update_rate_limit(current)

    @classmethod
    def from_cooldown(
        cls: Type[CooldownMappingT],
        rate: int,
        per: float,
        by: ConstructKey,
        cooldown_cls: Type[Cooldown] = Cooldown,
    ) -> CooldownMappingT:
        return cls(cooldown_cls(rate, per), by)


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
    by: ConstructKey,
    cls: Type[Cooldown] = Cooldown,
    mapping: Type[CooldownMapping] = CooldownMapping,
    retry_after_precision: int = 2,
) -> Callable[[Handler], Handler]:
    def wrapper(handler: Handler) -> Handler:
        cooldown_mapping = mapping.from_cooldown(rate, per, by, cooldown_cls=cls)

        @wraps(handler)
        async def actual_handler(request: web.Request) -> web.StreamResponse:
            retry_after = cooldown_mapping.update_rate_limit(request)

            if retry_after is None:
                return await handler(request)

            else:
                return create_cooldown_error(
                    round(retry_after, retry_after_precision)
                ).into_response()

        return actual_handler

    return wrapper
