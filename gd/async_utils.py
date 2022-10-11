from __future__ import annotations

from asyncio import AbstractEventLoop, all_tasks, gather, get_running_loop, run, wait
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    List,
    Type,
    TypeVar,
    Union,
    overload,
)

from iters.async_utils import async_iter, async_list
from typing_extensions import Literal, ParamSpec

from gd.typing import AnyException, AnyIterable, Nullary, is_error, is_instance

__all__ = (
    "run_blocking",
    "run",
    "gather",
    "gather_iterable",
    "wait",
    "cancel_all_tasks",
    "shutdown_loop",
    "awaiting",
    "run_iterables",
)

P = ParamSpec("P")
T = TypeVar("T")

E = TypeVar("E", bound=AnyException)

Result = Union[T, E]
AnyResult = Result[T, AnyException]


async def run_blocking(function: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    return await get_running_loop().run_in_executor(None, call_function(function, *args, **kwargs))


def call_function(function: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Nullary[T]:
    def call() -> T:
        return function(*args, **kwargs)

    return call


@overload
async def gather_iterable(
    awaitables: Iterable[Awaitable[T]], return_exceptions: Literal[False] = ...
) -> List[T]:
    ...


@overload
async def gather_iterable(
    awaitables: Iterable[Awaitable[T]], return_exceptions: Literal[True]
) -> List[AnyResult[T]]:
    ...


@overload
async def gather_iterable(
    awaitables: Iterable[Awaitable[T]], return_exceptions: bool
) -> List[AnyResult[T]]:
    ...


async def gather_iterable(
    awaitables: Iterable[Awaitable[T]],
    return_exceptions: bool = False,
) -> Union[List[T], List[AnyResult[T]]]:
    return await gather(*awaitables, return_exceptions=return_exceptions)


def cancel_all_tasks(loop: AbstractEventLoop) -> None:
    tasks = all_tasks(loop)

    for task in tasks:
        task.cancel()


def shutdown_loop(loop: AbstractEventLoop) -> None:
    if loop.is_closed():
        return

    loop.stop()

    try:
        cancel_all_tasks(loop)

        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(loop.shutdown_default_executor())

    except Exception:
        pass

    finally:
        loop.close()


async def awaiting(awaitable: Awaitable[T]) -> T:
    return await awaitable


async def run_iterables(
    iterables: AnyIterable[AnyIterable[T]], *ignore: Type[AnyException]
) -> AsyncIterator[T]:
    coroutines = [async_list(async_iter(iterable)) async for iterable in async_iter(iterables)]

    results = await gather_iterable(coroutines, return_exceptions=True)

    for result in results:
        if is_error(result):
            if is_instance(result, ignore):
                continue

            raise result

        else:
            for item in result:  # type: ignore
                yield item
