# XXX: this module is bound to fail at some point since it relies on scraping...

import re
from typing import Any, Iterator, Optional

from iters.iters import iter

try:
    from lxml.html import fromstring as from_string

except ImportError:
    print(
        "failed to import `lxml`; large portion of `newgrounds` functionality is not going to work."
    )

from typing_aliases import NormalError
from yarl import URL

from gd.constants import EMPTY
from gd.errors import InternalError
from gd.models import ArtistModel, SongModel
from gd.string_utils import concat_empty, remove_escapes

__all__ = (
    "find_song_model",
    "search_song_models",
    "search_artist_models",
    "search_artist_song_models",
)

UNQOUTED = r"[^\"']"
QUOTE = r"[\"']"
DIGIT = r"[0-9]"
SPACE = r"[ ]"

FILE_NAME = "filename"

DOWNLOAD_URL_PATTERN = f"{QUOTE}{FILE_NAME}{QUOTE}{SPACE}*:{SPACE}*{QUOTE}({UNQOUTED}+){QUOTE}"
DOWNLOAD_URL = re.compile(DOWNLOAD_URL_PATTERN)

FILE_SIZE = "filesize"

SIZE_PATTERN = f"{QUOTE}{FILE_SIZE}{QUOTE}{SPACE}*:{SPACE}*({DIGIT}+)"
SIZE = re.compile(SIZE_PATTERN)

OPEN_TAG = "<{}>"
CLOSE_TAG = "</{}>"

open_tag = OPEN_TAG.format
close_tag = CLOSE_TAG.format

TITLE = "title"

NAME_PATTERN = f"{open_tag(TITLE)}(.+){close_tag(TITLE)}"
NAME = re.compile(NAME_PATTERN)

ARTIST = "artist"

ARTIST_NAME_PATTERN = f"{QUOTE}{ARTIST}{QUOTE}{SPACE}*:{SPACE}*{QUOTE}({UNQOUTED}+){QUOTE}"
ARTIST_NAME = re.compile(ARTIST_NAME_PATTERN)

FACTOR = 1024
ROUNDING = 2


def megabytes(bytes: int) -> float:
    return round(bytes / FACTOR / FACTOR, ROUNDING)


CAN_NOT_FIND_SONG_MODEL = "can not find the song model"


def find_song_model(string: str, id: int) -> SongModel:
    string = remove_escapes(string)

    match = DOWNLOAD_URL.search(string)

    if match is None:
        raise ValueError(CAN_NOT_FIND_SONG_MODEL)

    download_url = URL(match.group(1))

    match = SIZE.search(string)

    if match is None:
        raise ValueError(CAN_NOT_FIND_SONG_MODEL)

    bytes = match.group(1)

    if bytes is None:
        raise InternalError  # TODO: message?

    size = megabytes(int(bytes))  # I do not really expect this to fail tbh

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


SONG_URL_PATH = r"""
.//a[@class="item-audiosubmission "]
""".strip()  # why on Earth is there a space at the end of the class?

DETAILS_PATH = r"""
.//div[@class="detail-title"]
""".strip()  # okay, fine, whatever

HREF = "href"

HTTPS = "https"

FIRST = 0
SECOND = 1
LAST = ~0


def search_song_models(string: str) -> Iterator[SongModel]:
    root = from_string(string)

    for a_element, div_element in zip(root.findall(SONG_URL_PATH), root.findall(DETAILS_PATH)):
        url = URL(a_element.attrib[HREF]).with_scheme(HTTPS)  # type: ignore

        id = int(url.parts[LAST])  # song ID is the last part of the URL

        h_element = div_element[FIRST]
        span_element = div_element[SECOND]

        name = empty_if_none(h_element.text) + concat_empty(  # preserve spacing
            empty_if_none(mark_element.text) + empty_if_none(mark_element.tail)
            for mark_element in h_element
        )

        artist_name = empty_if_none(span_element[FIRST].text).strip()

        if artist_name:  # artist name has to be non-empty
            yield SongModel(id=id, name=name, artist_name=artist_name)


def empty_if_none(option: Optional[str]) -> str:
    return EMPTY if option is None else option


ITEMS = "items"


def search_artist_song_models(data: Any, artist_name: str) -> Iterator[SongModel]:
    try:
        items = data[ITEMS].values()

    except NormalError:
        return

    for string in iter.chain_with(items).unwrap():  # type: ignore
        root = from_string(string)

        a_element = root.findall(SONG_URL_PATH)[FIRST]

        url = URL(a_element.attrib[HREF]).with_scheme(HTTPS)  # type: ignore

        id = int(url.parts[LAST])

        div_element = root.findall(DETAILS_PATH)[FIRST]

        h_element = div_element[FIRST]

        name = h_element.text

        if name:
            yield SongModel(id=id, name=name, artist_name=artist_name)


ARTIST_URL_PATH = r"""
.//div[@class="item-details-main"]/h4/a
""".strip()


def search_artist_models(string: str) -> Iterator[ArtistModel]:
    root = from_string(string)

    for a_element in root.findall(ARTIST_URL_PATH):
        artist_name = empty_if_none(a_element.text).strip()

        if artist_name:
            yield ArtistModel(name=artist_name)
