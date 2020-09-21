from functools import wraps

from gd.async_utils import acquire_loop, maybe_coroutine
from gd.debug_utils import time_execution_and_print
from gd.errors import MissingAccess
from gd.typing import (
    Any,
    Awaitable,
    Callable,
    Optional,
    Type,
    TypeVar,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from gd.abstract_entity import AbstractEntity  # noqa
    from gd.client import Client  # noqa

__all__ = (
    "benchmark",
    "cache_by",
    "impl_sync",
    "login_check",
    "login_check_object",
    "patch",
    "run_once",
    "sync",
)

T = TypeVar("T")
U = TypeVar("U")


def benchmark(function: Callable[..., T]) -> Callable[..., T]:
    @wraps(function)
    def inner(*args, **kwargs) -> T:
        return time_execution_and_print(function, *args, **kwargs)

    return inner


def cache_by(*names: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        @wraps(function)
        def wrapper(self, *args, **kwargs) -> T:
            actual = tuple(getattr(self, name) for name in names)

            try:
                cached = function._cached  # type: ignore

            except AttributeError:
                result = function(self, *args, **kwargs)

                function._cached = result  # type: ignore

                return result

            try:
                cached_by = function._cached_by  # type: ignore

            except AttributeError:
                function._cached_by = actual  # type: ignore

            else:
                if actual == cached_by:
                    return cached

            function._cached_by = actual  # type: ignore

            result = function(self, *args, **kwargs)

            function._cached = result  # type: ignore

            return result

        return wrapper

    return decorator


def sync(function: Callable[..., Union[Awaitable[T], T]]) -> Callable[..., Union[Awaitable[T], T]]:
    @wraps(function)
    def syncer(*args, **kwargs) -> T:
        return acquire_loop().run_until_complete(maybe_coroutine(function, *args, **kwargs))

    return syncer


def impl_sync(cls: Type[T]) -> Type[T]:
    try:
        old_get = cls.__getattr__  # type: ignore
    except AttributeError:

        def old_get(instance: T, name: str) -> None:
            raise AttributeError(f"{type(instance).__name__!r} has no attribute {name!r}")

    lookup = "sync_"

    def get_impl(instance: T, name: str) -> Any:
        if name.startswith(lookup):

            name = name[len(lookup) :]  # skip lookup part in name

            return sync(getattr(instance, name))

        else:
            return old_get(instance, name)

    cls.__getattr__ = get_impl  # type: ignore

    return cls


def login_check(function: Callable[..., T]) -> Callable[..., T]:
    @wraps(function)
    def wrapper(client_or_entity: Union["AbstractEntity", "Client"], *args, **kwargs) -> T:
        login_check_object(client_or_entity)
        return function(client_or_entity, *args, **kwargs)

    return wrapper


def login_check_object(client_or_entity: Union["AbstractEntity", "Client"]) -> None:
    client: "Client" = getattr(client_or_entity, "client", client_or_entity)

    if not client.is_logged():
        raise MissingAccess("Client is not logged in.")


def run_once(function: Callable[..., T]) -> Callable[..., T]:
    @wraps(function)
    def runner(*args, **kwargs) -> T:
        if not hasattr(function, "run_once_result"):
            function.run_once_result = function(*args, **kwargs)  # type: ignore

        return function.run_once_result  # type: ignore

    return runner


def patch(
    some_object: Any, name: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        nonlocal name

        if name is None:
            name = function.__name__

        setattr(some_object, name, function)

        return function

    return decorator
