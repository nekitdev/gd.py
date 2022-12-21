from __future__ import annotations

from functools import lru_cache, wraps
from operator import attrgetter as get_attribute_factory
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Tuple, TypeVar

from iters import iter
from typing_extensions import Concatenate, ParamSpec

from gd.async_utils import awaiting, run
from gd.errors import LoginRequired
from gd.typing import DecoratorIdentity, DynamicTuple

if TYPE_CHECKING:
    from gd.client import Client

__all__ = (
    "cache",
    "cache_by",
    "check_client_login",
    "check_login",
    "sync",
)

P = ParamSpec("P")
T = TypeVar("T")
S = TypeVar("S")

cache = lru_cache(None)

CACHE_BY_AT_LEAST_ONE = "`cache_by` expects at least one name to be provided"


def cache_by(*names: str) -> DecoratorIdentity[Callable[Concatenate[S, P], T]]:
    """Caches method calls based on object's attributes given by `names`."""

    if not names:
        raise ValueError(CACHE_BY_AT_LEAST_ONE)

    def decorator(function: Callable[Concatenate[S, P], T]) -> Callable[Concatenate[S, P], T]:
        get_attributes = iter(names).map(get_attribute_factory).tuple()

        cache: Dict[int, Tuple[T, DynamicTuple[Any]]] = {}

        @wraps(function)
        def wrap(self: S, *args: P.args, **kwargs: P.kwargs) -> T:
            actual = tuple(get_attribute(self) for get_attribute in get_attributes)

            key = id(self)

            if key in cache:
                cached, cached_by = cache[key]

                if actual == cached_by:
                    return cached

            result = function(self, *args, **kwargs)

            cache[key] = (result, actual)

            return result

        return wrap

    return decorator


def sync(function: Callable[P, Awaitable[T]]) -> Callable[P, T]:
    """Wraps the `function` to be called synchronously."""

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> T:
        return run(awaiting(function(*args, **kwargs)))

    return wrap


C = TypeVar("C", bound="Client")


def check_login(function: Callable[Concatenate[C, P], T]) -> Callable[Concatenate[C, P], T]:
    """Checks whether the `client` passed as the first argument is logged in."""

    @wraps(function)
    def wrap(client: C, *args: P.args, **kwargs: P.kwargs) -> T:
        check_client_login(client)

        return function(client, *args, **kwargs)

    return wrap


NOT_LOGGED_IN = "the client is not logged in"


def check_client_login(client: C) -> None:
    """Checks whether the `client` is logged in."""

    if not client.is_logged_in():
        raise LoginRequired(NOT_LOGGED_IN)
