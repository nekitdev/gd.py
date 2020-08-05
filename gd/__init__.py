"""Library that provides its users ability to interact
with the servers and the game of Geometry Dash.
"""

__title__ = "gd"
__author__ = "NeKitDS"
__copyright__ = "Copyright 2019-2020 NeKitDS"
__license__ = "MIT"
__version__ = "1.0.0rc0"

from gd.abstractentity import AbstractEntity
from gd.abstractuser import AbstractUser, LevelRecord
from gd.client import Client, DAILY, WEEKLY
from gd.colors import Color
from gd.colors import colors
from gd.comment import Comment
from gd.errors import *
from gd.friend_request import FriendRequest
from gd.icon_factory import factory, IconFactory
from gd.iconset import IconSet
from gd.level import Level
from gd.level_packs import Gauntlet, MapPack
from gd.logging import *
from gd.message import Message
from gd.model import *
from gd.rewards import Chest, Quest
from gd.session import Session
from gd.song import ArtistInfo, Author, Song
from gd.user import UserStats, User
from gd.version import *
from gd.utils.converter import Converter
from gd.utils.decorators import breakpoint
from gd.utils.enums import *
from gd.utils.filters import Filters
from gd.utils.http_request import HTTPClient
from gd.utils.params import *
from gd.utils.parser import Parser
from gd.utils.routes import Route
from gd.utils.xml_parser import AioXMLParser, XMLParser

from gd.utils.crypto.coders import Coder
from gd.utils.crypto.xor_cipher import XORCipher as xor

from gd._jokes import *  # idk

from gd.utils import tasks

from gd import (
    api,  # non-server GD API.
    events,  # event-related functions and classes.
    memory,  # functions for interacting with memory.
    server,  # gd.api merged into gd.py.
    typing,  # various utils for typing gd.py.
    utils,  # different useful utils.
)
