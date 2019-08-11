__title__ = 'gd'
__author__ = 'NeKitDS'
__copyright__ = 'Copyright 2019 NeKitDS'
__license__ = 'MIT'
__version__ = '0.7.1'

from collections import namedtuple
import logging

from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser
from .client import Client
from .comment import Comment
from .errors import *
from .friend_request import FriendRequest
from .iconset import IconSet
from .level import Level
from .message import Message
from .session import GDSession
from .song import Song
from .unreguser import UnregisteredUser
from .user import User
from .graphics.colors import Colour, Color, colors
from .utils.captcha_solver import Captcha
from .utils.context import context
from .utils.enums import *
from .utils.gdpaginator import paginate, Paginator
from .utils.http_request import HTTPClient
from .utils.params import Parameters
from .utils.crypto.coders import Coder
from .utils.crypto.xor_cipher import XORCipher
from .utils.context import context
from .utils import run  # since asyncio.run() was introduced in 3.7, we have a run-like function.

log = logging.getLogger(__name__)

def _gen_version_details():
    ver = __version__
    cases = {
        'a' in ver: ('a', 'alpha'),
        'b' in ver: ('b', 'beta'),
        'rc' in ver: ('rc', 'candidate')
    }
    # we should not care about the separator if the releaselevel is 'final'
    splitter, releaselevel = cases.get(True, (' ', 'final'))
    splitted = ver.split(splitter)
    serial = 0
    if len(splitted) > 1:  # if there's a serial
        _, s = splitted
        serial = int(s)
    major, minor, micro = map(int, splitted[0].split('.'))
    VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
    return VersionInfo(
        major=major, minor=minor, micro=micro, releaselevel=releaselevel, serial=serial
    )
    
version_info = _gen_version_details()


def setup_basic_logging():
    """Function that sets up logs of the module,
    with the following format:
    [INFO] (time) {gd.some_module}: Some info message.
    """
    hdlr = logging.StreamHandler()
    hdlr.setFormatter(
        logging.Formatter('[%(levelname)s] (%(asctime)s) {%(name)s}: %(message)s')
    )
    log.setLevel(logging.DEBUG)
    log.addHandler(hdlr)

# setting up the NullHandler here
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
