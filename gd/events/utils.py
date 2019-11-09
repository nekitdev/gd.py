from os import _exit

from .scanner import (
    AbstractScanner as scanner, run as run_loop,
    shutdown_loop, all_listeners, thread, loop as _loop
)

from .. import utils

__all__ = ('exit', 'disable', 'enable', 'add_client', 'start', 'run', 'attach_to_loop')


def exit(status: int = 0):
    disable()
    _exit(status)

def disable():
    try:
        shutdown_loop(_loop)
        thread.join()
    except RuntimeError:
        pass

    for scan in utils.get_instances_of(scanner):
        scan.close()

def enable():
    for listener in all_listeners:
        listener.enable()

def add_client(client):
    for listener in all_listeners:
        listener.add_client(client)

def attach_to_loop(loop):
    for listener in all_listeners:
        listener.attach_to_loop(loop)

def run(loop):
    run_loop(loop)

def start():
    thread.start()
