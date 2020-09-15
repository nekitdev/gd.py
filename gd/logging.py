import logging
from pathlib import Path

from gd.typing import IO, Optional, Union

__all__ = (
    "enable_file_handler_for",
    "enable_stream_handler_for",
    "get_logger",
    "log",
    "setup_logging",
)

ALL_STYLES = ("%", "{", "$")

DEFAULT_LOG_FORMAT = "[{levelname}] ({asctime}) [{name}] {module}.{funcName}:{lineno}: {message}"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)


def get_module_logger() -> logging.Logger:
    return get_logger(__name__.split(".")[0])


def attempt_all_format_styles(format_string: str) -> logging.Formatter:
    for style in ALL_STYLES:
        try:
            return logging.Formatter(format_string, style=style)

        except ValueError:
            pass

    else:
        raise ValueError(f"Format string {format_string!r} is invalid.")


def add_formatter_and_handler(
    logger: logging.Logger,
    handler: logging.Handler,
    level: int = logging.DEBUG,
    format_string: Optional[str] = None,
) -> None:
    if format_string is None:
        format_string = DEFAULT_LOG_FORMAT

    handler.setFormatter(attempt_all_format_styles(format_string))

    handler.setLevel(level)

    logger.addHandler(handler)


def enable_file_handler_for(
    logger: logging.Logger,
    filename: Union[Path, str],
    level: int = logging.DEBUG,
    format_string: Optional[str] = None,
) -> None:
    add_formatter_and_handler(
        logger=logger,
        handler=logging.FileHandler(filename),
        level=level,
        format_string=format_string,
    )


def enable_stream_handler_for(
    logger: logging.Logger,
    stream: Optional[IO] = None,
    level: int = logging.DEBUG,
    format_string: Optional[str] = None,
) -> None:
    add_formatter_and_handler(
        logger=logger,
        handler=logging.StreamHandler(stream),
        level=level,
        format_string=format_string,
    )


def setup_logging(
    level: int = logging.DEBUG,
    format_string: Optional[str] = None,
    stream: Optional[IO] = None,
    filename: Optional[str] = None,
) -> None:
    if filename is None:
        enable_stream_handler_for(
            logger=log, stream=stream, level=level, format_string=format_string
        )

    else:
        enable_file_handler_for(
            logger=log, filename=filename, level=level, format_string=format_string
        )


log = get_module_logger()

log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())
