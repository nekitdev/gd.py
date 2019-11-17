"""Library that provides its users ability to interact with servers of Geometry Dash."""

__title__ = 'gd'
__author__ = 'NeKitDS'
__copyright__ = 'Copyright 2019 NeKitDS'
__license__ = 'MIT'
__version__ = '0.10.1'

from collections import namedtuple
import logging

from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser, LevelRecord
from .client import Client
from .colors import Colour, Color
from .colors import colors
from .comment import Comment
from .errors import *
from .friend_request import FriendRequest
from .iconset import IconSet
from .level import Level
from .level_packs import Gauntlet, MapPack
from .message import Message
from .session import GDSession
from .song import Song
from .unreguser import UnregisteredUser
from .user import UserStats, User
from .events import exit
from .utils.captcha_solver import Captcha
from .utils.enums import *
from .utils.filters import Filters
from .utils.gdpaginator import paginate, Paginator
from .utils.http_request import http, HTTPClient
from .utils.params import *
from .utils.save_parser import Save, SaveParser
from .utils.crypto.coders import Coder
from .utils.crypto.xor_cipher import XORCipher

from ._jokes import jokes  # why not?...

from .utils._async import synchronize

from . import api  # this package contains actual non-server gd API.
from . import events  # this package contains event-related functions and classes.
from . import utils  # since asyncio.run() was introduced in 3.7, we have utils.run() function.


log = logging.getLogger(__name__)


VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

def make_version_details(ver: str):
    cases = {
        'a' in ver: ('a', 'alpha'),
        'b' in ver: ('b', 'beta'),
        'rc' in ver: ('rc', 'candidate'),
        'f' in ver: ('f', 'final')
    }

    # we should not care about the separator if the releaselevel is 'final'
    splitter, releaselevel = cases.get(True, (' ', 'final'))
    splitted = ver.split(splitter)

    serial = 0
    if len(splitted) > 1:  # if there's a serial
        _, s = splitted
        serial = serial if not s else int(s)

    major, minor, micro = map(int, splitted[0].split('.'))

    return VersionInfo(
        major=major, minor=minor, micro=micro, releaselevel=releaselevel, serial=serial
    )

version_info = make_version_details(__version__)


def setup_logging(level: int = logging.DEBUG, *, stream=None, file=None, formatter=None):
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
    handler = (
        logging.StreamHandler(stream) if file is None else logging.FileHandler(file)
    )

    if formatter is None:
        formatter = '[%(levelname)s] (%(asctime)s) {%(name)s}: %(message)s'

    handler.setFormatter(
        logging.Formatter(formatter)
    )

    log.addHandler(handler)

    log.setLevel(level)

# setting up the NullHandler here
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

log.addHandler(NullHandler())


# delete not required stuff
del NullHandler, namedtuple
