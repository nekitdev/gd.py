import asyncio

from .search_utils import find, get
from .wrap_tools import benchmark, check


def run(coro, *, debug: bool = False, raise_exceptions: bool = False):
    if asyncio._get_running_loop() is not None:
        raise RuntimeError('Can not perform gd.utils.run() in a running event loop.')
    if not asyncio.iscoroutine(coro):
        raise ValueError(f"A coroutine was expected, got {coro!r}.")
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)
        return loop.run_until_complete(coro)
    finally:
        try:
            _cancel_all_tasks(loop, raise_exceptions=raise_exceptions)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()

def _cancel_all_tasks(loop, raise_exceptions: bool = False):
    try:
        to_cancel = asyncio.all_tasks(loop)
    except AttributeError:  # py < 3.7
        to_cancel = asyncio.Task.all_tasks(loop)
    if not to_cancel:
        return
    for task in to_cancel:
        task.cancel()
    loop.run_until_complete(
        asyncio.gather(*to_cancel, loop=loop, return_exceptions=True)
    )
    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None and raise_exceptions:
            loop.call_exception_handler({
                'message': 'Unhandled exception during gd.utils.run() shutdown',
                'exception': task.exception(),
                'task': task,
            })
