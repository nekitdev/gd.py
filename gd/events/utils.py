from os import _exit

from .scanner import AbstractScanner, all_listeners

from .. import utils

__all__ = ('exit', 'disable', 'enable', 'add_client')


def exit(status: int = 0):
    disable()
    _exit(status)

def disable():
    for scanner in utils.get_instances_of(AbstractScanner):
        scanner.close()

def enable():
    for listener in all_listeners:
        listener.start()

def add_client(client):
    for listener in all_listeners:
        listener.add_client(client)

def attach_to_loop(loop):
    for listener in all_listeners:
        listener.attach_to_loop(loop)
