from asyncio import AbstractEventLoop, all_tasks, get_running_loop
from typing import Callable, TypeVar

from typing_aliases import NormalError, Nullary
from typing_extensions import ParamSpec

__all__ = ("run_blocking", "cancel_all_tasks", "shutdown_loop")

P = ParamSpec("P")
T = TypeVar("T")


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

    except NormalError:
        pass

    finally:
        loop.close()
