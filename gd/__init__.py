"""Library that provides its users ability to interact
with the servers and the game of Geometry Dash.
"""

__title__ = "gd"
__author__ = "nekitdev"
__copyright__ = "Copyright 2019-2020 nekitdev"
__license__ = "MIT"
__version__ = "1.0.0rc1"

from gd import api  # non-server GD API.
from gd import crypto  # cryptography and encoding utilites.
from gd import datetime  # date and time [de]serializing utilites.
from gd import events  # event-related functions and classes.
from gd import http  # HTTP requests module.
from gd import image  # sprites handling and icon factory.
from gd import json  # JSON utilities.
from gd import memory  # functions for interacting with memory.
from gd import model_backend  # backend for gd.py models.
from gd import server  # REST API wrapper around gd.py.
from gd import tasks  # background tasks implementation
from gd import utils  # different useful utilities.
from gd.abstract_entity import *
from gd.client import *
from gd.color import *
from gd.comment import *
from gd.converters import *
from gd.decorators import *
from gd.enums import *
from gd.errors import *
from gd.filters import *
from gd.friend_request import *
from gd.http import *
from gd.level import *
from gd.level_packs import *
from gd.logging import *
from gd.message import *
from gd.model import *
from gd.rewards import *
from gd.session import *
from gd.song import *
from gd.user import *
from gd.version import *
from gd.xml_parser import *
