from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Tuple, TypeVar, Union

from attrs import Attribute, field, frozen
from funcs.decorators import wraps
from funcs.getters import attribute_getter
from typing_aliases import DynamicTuple
from typing_extensions import Concatenate, ParamSpec, final

from gd.errors import LoginRequired

if TYPE_CHECKING:
    from gd.client import Client

__all__ = ("cache_by", "check_client_login", "check_login")

P = ParamSpec("P")
T = TypeVar("T")
S = TypeVar("S")

CACHE_BY_AT_LEAST_ONE = "`cache_by` expects at least one name to be provided"

Names = DynamicTuple[str]
Values = Union[Any, DynamicTuple[Any]]


@final
@frozen()
class CacheBy:
    names: Names = field()

    @names.validator
    def validate_names(self, attribute: Attribute[Names], value: Names) -> None:
        if not value:
            raise ValueError(CACHE_BY_AT_LEAST_ONE)

    def __call__(self, function: Callable[Concatenate[S, P], T]) -> Callable[Concatenate[S, P], T]:
        get_attributes = attribute_getter(*self.names)

        cache: Dict[int, Tuple[T, Values]] = {}

        @wraps(function)
        def wrap(self: S, *args: P.args, **kwargs: P.kwargs) -> T:
            actual = get_attributes(self)

            key = id(self)

            if key in cache:
                cached, cached_by = cache[key]

                if actual == cached_by:
                    return cached

            result = function(self, *args, **kwargs)

            cache[key] = (result, actual)

            return result

        return wrap


def cache_by(*names: str) -> CacheBy:
    return CacheBy(names)


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
