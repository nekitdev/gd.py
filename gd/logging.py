import logging

from gd.typing import Any, Optional

__all__ = ("get_logger", "setup_logging", "log")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)


def get_module_logger():
    return get_logger(__name__.split(".").pop(0))


def setup_logging(
    level: int = logging.DEBUG,
    *,
    stream: Any = None,
    file: Any = None,
    formatter: Optional[str] = None,
) -> None:
    """Function that sets up logs of the module.

    Parameters
    ----------
    level: :class:`int`
        Level to set.

    stream: `Any`
        Stream to log messages into. ``stderr`` by default.

    file: `Any`
        File to log messages to. If not given, messages are logged into the ``stream``.

    formatter: :class:`str`
        Formatter to use. ``[LEVEL] (time) {gd.module}: Message`` by default.
    """
    handler = logging.StreamHandler(stream) if file is None else logging.FileHandler(file)

    if formatter is None:
        formatter = "[%(levelname)s] (%(asctime)s) {%(name)s}: %(message)s"

    handler.setFormatter(logging.Formatter(formatter))

    log.addHandler(handler)

    log.setLevel(level)


log = get_module_logger()
log.addHandler(logging.NullHandler())
