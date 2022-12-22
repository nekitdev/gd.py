from __future__ import annotations

from asyncio import AbstractEventLoop, all_tasks, get_running_loop, run, wait
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    Type,
    TypeVar,
    Union,
)

from iters.async_utils import async_iter, async_list
from iters.concurrent import collect_iterable_with_errors
from typing_extensions import ParamSpec

from gd.typing import AnyException, AnyIterable, Nullary, is_error, is_instance

__all__ = (
    "run_blocking",
    "run",
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

    results = await collect_iterable_with_errors(coroutines)

    for result in results:
        if is_error(result):
            if is_instance(result, ignore):
                continue

            raise result

        else:
            for item in result:  # type: ignore
                yield item
