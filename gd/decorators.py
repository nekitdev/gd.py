from functools import lru_cache, wraps
from operator import attrgetter

from gd.async_utils import get_not_running_loop, maybe_coroutine
from gd.code_utils import time_execution_and_print
from gd.errors import LoginRequired
from gd.typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Type, TypeVar, Union

if TYPE_CHECKING:
    from gd.abstract_entity import AbstractEntity  # noqa
    from gd.client import Client  # noqa

__all__ = (
    "benchmark",
    "cache",
    "cache_by",
    "login_check",
    "login_check_object",
    "patch",
    "run_once",
    "sync",
    "synchronize",
)

T = TypeVar("T")


def benchmark(function: Callable[..., T]) -> Callable[..., T]:
    """Benchmark time spent to call ``function``.
    :func:`~gd.utils.time_execution_and_print` is used internally.
    """

    @wraps(function)
    def inner(*args, **kwargs) -> T:
        return time_execution_and_print(function, *args, **kwargs)

    return inner


cache = lru_cache(None)


def cache_by(*names: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache ``function`` result by object's attributes given by ``names``."""

    if not names:
        raise ValueError("@cache_by requires at least one name to be provided.")

    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        get_attrs = tuple(attrgetter(name) for name in names)

        name = function.__name__

        if not name.isidentifier():
            name = f"unnamed_{id(function):x}"

        cached_attr = f"_{name}_cached"
        cached_by_attr = f"_{name}_cached_by"

        @wraps(function)
        def wrapper(self, *args, **kwargs) -> T:
            actual = tuple(get_attr(self) for get_attr in get_attrs)

            try:
                cached = getattr(self, cached_attr)
                cached_by = getattr(self, cached_by_attr)

            except AttributeError:
                pass

            else:
                if actual == cached_by:
                    return cached

            result = function(self, *args, **kwargs)

            setattr(self, cached_attr, result)
            setattr(self, cached_by_attr, actual)

            return result

        return wrapper

    return decorator


def sync(function: Callable[..., Union[Awaitable[T], T]]) -> Callable[..., T]:
    """Wrap ``function`` to be called synchronously."""

    @wraps(function)
    def syncer(*args, **kwargs) -> T:
        return get_not_running_loop().run_until_complete(maybe_coroutine(function, *args, **kwargs))

    return syncer


def synchronize(cls: Type[T]) -> Type[T]:
    """Implement ``sync_<name>`` functions for class ``cls`` to synchronously call methods."""
    try:
        old_get_attribute = cls.__getattr__  # type: ignore

    except AttributeError:

        def old_get_attribute(instance: T, name: str) -> None:
            raise AttributeError(f"{type(instance).__name__!r} has no attribute {name!r}")

    lookup = "sync_"

    def get_attribute(instance: T, name: str) -> Any:
        if name.startswith(lookup):

            name = name[len(lookup) :]  # skip lookup part in name

            return sync(getattr(instance, name))

        else:
            return old_get_attribute(instance, name)

    cls.__getattr__ = get_attribute  # type: ignore

    return cls


def login_check(function: Callable[..., T]) -> Callable[..., T]:
    """Wrap ``function`` for :class:`~gd.AbstractEntity` or :class:`~gd.Client`
    to check if the client is logged in.
    """

    @wraps(function)
    def wrapper(client_or_entity: Union["AbstractEntity", "Client"], *args, **kwargs) -> T:
        login_check_object(client_or_entity)

        return function(client_or_entity, *args, **kwargs)

    return wrapper


def login_check_object(client_or_entity: Union["AbstractEntity", "Client"]) -> None:
    """Check whether :class:`~gd.AbstractEntity` or :class:`~gd.Client` have logged in client."""
    client: "Client" = getattr(client_or_entity, "client", client_or_entity)

    if not client.is_logged():
        raise LoginRequired("Client is not logged in.")


def run_once(function: Callable[..., T]) -> Callable[..., T]:
    """Execute ``function`` once, cache the result and return it on other calls."""

    @wraps(function)
    def runner(*args, **kwargs) -> T:
        if not hasattr(function, "run_once_result"):
            function.run_once_result = function(*args, **kwargs)  # type: ignore

        return function.run_once_result  # type: ignore

    return runner


def patch(
    some_object: Any, name: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Patch ``name`` method or function of ``some_object`` with ``function``."""

    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        nonlocal name

        if name is None:
            name = function.__name__

        setattr(some_object, name, function)

        return function

    return decorator
