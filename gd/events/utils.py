import asyncio
from os import _exit

from .scanner import (
    AbstractScanner as scanner, run as run_loop, get_loop,
    shutdown_loop, all_listeners, thread, update_thread_loop, set_loop
)

from .._typing import Client

from .. import utils

__all__ = ('exit', 'disable', 'enable', 'add_client', 'start', 'run', 'attach_to_loop')


def exit(status: int = 0) -> None:
    disable()
    _exit(status)


def disable() -> None:
    try:
        shutdown_loop(get_loop())
        thread.join()
    except RuntimeError:
        pass

    try:
        scanners = utils.get_instances_of(scanner)
    except Exception:
        scanners = all_listeners

    for scan in scanners:
        scan.close()


def enable() -> None:
    for listener in all_listeners:
        listener.enable()


def add_client(client: Client) -> None:
    for listener in all_listeners:
        listener.add_client(client)


def attach_to_loop(loop: asyncio.AbstractEventLoop) -> None:
    update_thread_loop(thread, loop)

    set_loop(loop)

    for listener in all_listeners:
        listener.attach_to_loop(loop)


def run(loop: asyncio.AbstractEventLoop) -> None:
    run_loop(loop)


def start() -> None:
    thread.start()
