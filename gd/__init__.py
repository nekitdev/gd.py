"""Library that provides its users ability to interact
with the servers and the game of Geometry Dash.
"""

__title__ = 'gd'
__author__ = 'NeKitDS'
__copyright__ = 'Copyright 2019-2020 NeKitDS'
__license__ = 'MIT'
__version__ = '0.10.4'

from collections import namedtuple
import logging
import re

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
    api,     # non-server GD API.
    events,  # event-related functions and classes.
    image,   # functions for working with images.
    server,  # gd.api merged into gd.py
    utils,   # different useful utils.
    typing   # various utils for typing gd.py.
)

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

_normal_re = (
r'^\s*(?:'
    r'(?P<major>\d+)'
    r'(?P<split>[\.-])?'
    r'(?P<minor>\d+)?'
    r'(?P=split)?'
    r'(?P<micro>\d+)?'
    r'(?P<releaselevel>a|b|rc|f|dev)?'
    r'(?P<serial>\d+)?'
r')\s*$'
)
_compiled_re = re.compile(_normal_re, re.MULTILINE)


def make_version_details(ver: str) -> VersionInfo:
    match = _compiled_re.match(ver)

    if match is None:
        return VersionInfo(0, 0, 0, 'final', 0)

    args = {}

    for key, value in match.groupdict().items():
        if key == 'split':
            continue

        elif key == 'releaselevel':
            if value is None:
                value = 'f'

            value = {
                'a': 'alpha',
                'b': 'beta',
                'rc': 'candidate',
                'f': 'final',
                'dev': 'developer'
            }.get(value, 'final')

        elif value is None:
            value = 0

        else:
            value = int(value)

        args[key] = value

    return VersionInfo(**args)


version_info = make_version_details(__version__)


# setting up the NullHandler here
try:
    from logging import NullHandler

# in case there is no NullHandler
except ImportError:  # pragma: no cover
    # create custom class
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# log is from gd.logging.
log.addHandler(NullHandler())


# delete not required stuff
del NullHandler
del logging, namedtuple, re
