from functools import wraps

import iters

from gd.typing import Any, AsyncIterable, Callable, Coroutine, List, TypeVar

__all__ = ("AsyncIter", "async_iter", "async_iterable", "async_next")

T = TypeVar("T")


class AsyncIter(iters.AsyncIter[T]):
    def __await__(self) -> Coroutine[Any, None, List[T]]:
        # await iterator -> await iterator.list()
        return self.list().__await__()


def async_iterable(function: Callable[..., AsyncIterable[T]]) -> Callable[..., AsyncIter[T]]:
    @wraps(function)
    def wrapper(*args, **kwargs) -> AsyncIter[T]:
        return AsyncIter(function(*args, **kwargs))

    return wrapper


async_iter = AsyncIter
async_next = iters.async_next_unchecked
