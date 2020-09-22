"""Library that provides its users ability to interact
with the servers and the game of Geometry Dash.
"""

__title__ = "gd"
__author__ = "NeKitDS"
__copyright__ = "Copyright 2019-2020 NeKitDS"
__license__ = "MIT"
__version__ = "1.0.0rc1"

from gd.abstract_entity import *
from gd.client import *
from gd.color import *
from gd.comment import *
from gd.decorators import *
from gd.enums import *
from gd.errors import *
from gd.filters import *
from gd.friend_request import *
from gd.http import *
from gd.icon_factory import *
from gd.level import *
from gd.level_packs import *
from gd.logging import *
from gd.message import *
from gd.model import *
from gd.session import *
from gd.rewards import *
from gd.song import *
from gd.user import *
from gd.version import *
from gd.xml_parser import *

from gd._jokes import *

from gd import (
    api,  # non-server GD API.
    crypto,  # cryptography and encoding utilites.
    datetime,  # date and time [de]serializing utilites.
    events,  # event-related functions and classes.
    http,  # HTTP requests module.
    json,  # JSON utilities.
    memory,  # functions for interacting with memory.
    model_backend,  # backend for gd.py models.
    server,  # REST API wrapper around gd.py.
    tasks,  # background tasks implementation
    utils,  # different useful utilities.
)
