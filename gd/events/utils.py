import asyncio
import atexit

from gd.events.listener import (
    run as run_loop,
    get_loop,
    shutdown_loop,
    all_listeners,
    thread,
    update_thread_loop,
    set_loop,
)

from gd.typing import Optional

__all__ = ("disable", "start", "run", "attach_to_loop")


def disable() -> None:
    """Disable the running thread and shutdown the loop, as well as all listeners.
    This function is intended to be called at the end of programs,
    because gd.events.start() can not be called after it."""
    try:
        shutdown_loop(get_loop())
        thread.join()
    except (RuntimeError, ValueError):
        pass

    for listener in all_listeners:
        listener.close()


def attach_to_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Attach new loop to all listeners, thread and set it as a main loop.
    This can be used in order to use your own loop for running events listeners:

    .. code-block:: python3

        from discord.ext import commands
        import gd

        bot = commands.Bot(command_prefix="?")

        gd.events.attach_to_loop(bot.loop)

        ...

        bot.run("TOKEN")  # this will also run listeners

    .. warning::

        This function should be called **before** any ``client.listen_for`` calls.
    """

    update_thread_loop(thread, loop)

    set_loop(loop)

    for listener in all_listeners:
        listener.attach_to_loop(loop)


def run(loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Run listeners in a given loop."""
    if loop is None:
        loop = get_loop()

    attach_to_loop(loop)
    run_loop(loop)


def start() -> None:
    """Start the listener thread. This can be run only once."""
    thread.start()


atexit.register(disable)
