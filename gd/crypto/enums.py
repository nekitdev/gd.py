from enum import Enum

from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.strings.constants import EMPTY


class Key(Enum):
    """Represents keys used in *XOR* (`^`) ciphers."""

    SAVE = 11
    """The key used to encode *save* data."""


class CyclicKey(Enum):
    """Represents keys used in cyclic *XOR* (`^`) ciphers."""

    MESSAGE = "14251"
    """The key used for encoding message content."""

    QUESTS = "19847"
    """The key used for encoding quests."""

    LEVEL_PASSWORD = "26364"
    """The key used for encoding level passwords."""

    COMMENT = "29481"
    """The key used for generating comment checks."""

    USER_PASSWORD = "37526"
    """The key used for encoding user passwords."""

    LEVEL_LEADERBOARD = "39673"
    """The key used for generating level leaderboard checks."""

    LEVEL = "41274"
    """The key used for encoding level information."""

    LIKE_RATE = "58281"
    """The key used for generating like/rate checks."""

    CHESTS = "59182"
    """The key used for encoding chests."""

    USER_LEADERBOARD = "85271"
    """The key used for generating user leaderboard checks."""

    def __init__(
        self, value: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
    ) -> None:
        self.bytes = value.encode(encoding, errors)


class Salt(Enum):
    """Represents salts used in hashing."""

    LEVEL = "xI25fpAapCQg"
    """The salt used for generating level checks and computing level hashes."""

    COMMENT = "xPT6iUrtws0J"
    """The salt used for generating comment checks."""

    LIKE_RATE = "ysg6pUrtjn0J"
    """The salt used for generating like/rate checks."""

    USER_LEADERBOARD = "xI35fsAapCRg"
    """The salt used for generating user leaderboard checks."""

    LEVEL_LEADERBOARD = "yPg6pUrtWn0J"
    """The salt used for generating level leaderboard checks."""

    QUESTS = "oC36fpYaPtdg"
    """The salt used for computing quest hashes."""

    CHESTS = "pC26fpYaQCtg"
    """The salt used for computing chest hashes."""

    PASSWORD = "mI29fmAnxgTs"
    """The salt used for hashing passwords."""

    EMPTY = EMPTY
    """The empty salt."""

    def __init__(
        self,
        string: str,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        self.string = string
        self.bytes = string.encode(encoding, errors)
