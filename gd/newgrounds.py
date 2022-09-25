import re

from yarl import URL

from gd.errors import InternalError
from gd.models import SongModel

__all__ = ("find_song_model",)

UNQOUTED = r"[^\"']"
QUOTE = r"[\"']"
DIGIT = r"[0-9]"
SPACE = r"[ ]"

DOWNLOAD_URL_BASE = "https://audio.ngfiles.com/"

DOWNLOAD_URL_PATTERN = f"{re.escape(DOWNLOAD_URL_BASE)}{UNQOUTED}+"
DOWNLOAD_URL = re.compile(DOWNLOAD_URL_PATTERN)

FILE_SIZE = "filesize"

SIZE_PATTERN = f"{QUOTE}{FILE_SIZE}{QUOTE}{SPACE}*:{SPACE}*({DIGIT}+)"
SIZE = re.compile(SIZE_PATTERN)

OPEN_TAG = "<{}>"
CLOSE_TAG = "</{}>"

CONTENT = r"[^<>]"

open_tag = OPEN_TAG.format
close_tag = CLOSE_TAG.format

TITLE = "title"

NAME_PATTERN = f"{open_tag(TITLE)}({CONTENT}+){close_tag(TITLE)}"
NAME = re.compile(NAME_PATTERN)

ARTIST = "artist"

ARTIST_NAME_PATTERN = f"{QUOTE}{ARTIST}{QUOTE}{SPACE}*:{SPACE}*{QUOTE}({UNQOUTED}+){QUOTE}"
ARTIST_NAME = re.compile(ARTIST_NAME_PATTERN)

FACTOR = 1024.0
ROUNDING = 2


def megabytes(bytes: float) -> float:
    return round(bytes / FACTOR / FACTOR, ROUNDING)


CAN_NOT_FIND_SONG_MODEL = "can not find the song model"


def find_song_model(string: str, id: int) -> SongModel:
    match = DOWNLOAD_URL.search(string)

    if match is None:
        raise ValueError(CAN_NOT_FIND_SONG_MODEL)

    download_url = URL(match.group())

    match = SIZE.search(string)

    if match is None:
        raise ValueError(CAN_NOT_FIND_SONG_MODEL)

    bytes = match.group(1)

    if bytes is None:
        raise InternalError  # TODO: message?

    size = megabytes(float(bytes))

    match = ARTIST_NAME.search(string)

    if match is None:
        raise ValueError(CAN_NOT_FIND_SONG_MODEL)

    artist_name = match.group(1)

    if artist_name is None:
        raise InternalError  # TODO: message?

    match = NAME.search(string)

    if match is None:
        raise ValueError(CAN_NOT_FIND_SONG_MODEL)

    name = match.group(1)

    if name is None:
        raise InternalError  # TODO: message?

    name = name.strip()

    return SongModel(
        id=id, name=name, artist_name=artist_name, size=size, download_url=download_url
    )
