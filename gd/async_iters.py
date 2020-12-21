from functools import wraps

from iters import AsyncIter, async_next_unchecked

from gd.typing import Any, AsyncIterable, Callable, Generator, Iterable, List, TypeVar, Union

__all__ = ("AwaitableIterator", "async_iter", "async_next", "awaitable_iterator")

T = TypeVar("T")

AnyIterable = Union[AsyncIterable[T], Iterable[T]]


class AwaitableIterator(AsyncIter[T]):
    def __await__(self) -> Generator[Any, None, List[T]]:
        # await iterator -> await iterator.list()
        return self.list().__await__()


def awaitable_iterator(
    function: Callable[..., AnyIterable[T]]
) -> Callable[..., AwaitableIterator[T]]:
    @wraps(function)
    def wrapper(*args, **kwargs) -> AwaitableIterator[T]:
        return AwaitableIterator(function(*args, **kwargs))

    return wrapper


async_iter = AwaitableIterator
async_next = async_next_unchecked
