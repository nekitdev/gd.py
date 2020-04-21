"""Library that provides its users ability to interact
with the servers and the game of Geometry Dash.
"""

__title__ = "gd"
__author__ = "NeKitDS"
__copyright__ = "Copyright 2019-2020 NeKitDS"
__license__ = "MIT"
__version__ = "0.10.5"

from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser, LevelRecord
from .client import Client, DAILY, WEEKLY
from .colors import Color
from .colors import colors
from .comment import Comment
from .errors import *
from .friend_request import FriendRequest
from .iconset import IconSet
from .level import Level
from .level_packs import Gauntlet, MapPack
from .logging import *
from .message import Message
from .session import Session
from .song import ArtistInfo, Author, Song
from .user import UserStats, User
from .version import *
from .utils.enums import *
from .utils.filters import Filters
from .utils.http_request import HTTPClient
from .utils.params import *
from .utils.parser import Parser
from .utils.save_parser import Save, SaveParser

from .utils.crypto.coders import Coder
from .utils.crypto.xor_cipher import XORCipher as xor

from ._jokes import *  # idk

from .utils._async import synchronize
from .utils import tasks

from . import (
    api,  # non-server GD API.
    events,  # event-related functions and classes.
    image,  # functions for working with images.
    server,  # gd.api merged into gd.py
    utils,  # different useful utils.
    typing,  # various utils for typing gd.py.
)
