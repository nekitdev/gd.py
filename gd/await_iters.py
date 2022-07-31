from functools import wraps
from typing import Callable, Generator, List, TypeVar

from iters.async_iters import AsyncIter
from typing_extensions import ParamSpec

from gd.typing import AnyIterable

__all__ = ("AwaitIter", "await_iter", "wrap_await_iter")

P = ParamSpec("P")
T = TypeVar("T", covariant=True)


class AwaitIter(AsyncIter[T]):
    def __await__(self) -> Generator[None, None, List[T]]:
        return self.list().__await__()


await_iter = AwaitIter


def wrap_await_iter(function: Callable[P, AnyIterable[T]]) -> Callable[P, AwaitIter[T]]:
    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> AwaitIter[T]:
        return await_iter(function(*args, **kwargs))

    return wrap
