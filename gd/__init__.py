"""An API wrapper for Geometry Dash written in Python."""

__description__ = "An API wrapper for Geometry Dash written in Python."
__url__ = "https://github.com/nekitdev/gd.py"

__title__ = "gd"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "2.0.0-dev.0"

from gd import (
    api,
    binary,
    crypto,
    entities,
    enums,
    events,
    http,
    images,
    memory,
    primitives,
    schema,
    time,
)
from gd.clients import Client

__all__ = (
    # libraries
    "api",
    "binary",
    "crypto",
    "entities",
    "enums",
    "events",
    "http",
    "images",
    "memory",
    "primitives",
    "schema",
    "time",
    # client
    "Client",
)
