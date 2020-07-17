"""This module is used for Newgrounds parsing."""

from collections import namedtuple
from itertools import chain
import re

from yarl import URL

from gd.utils.parser import ExtDict
from gd.logging import get_logger
from gd.typing import Dict, HTMLElement, List, TypeVar, Union, XMLElement

log = get_logger(__name__)

use_lxml, Element = False, XMLElement

try:
    from lxml import html

    use_lxml, Element = True, HTMLElement

except ImportError:
    try:
        from html5lib import parse
    except ImportError:
        log.warning("Failed to import lxml and html5lib. Newgrounds parsing will not be supported.")

__all__ = (
    "re_link",
    "re_name",
    "re_author",
    "re_size",
    "re_attrib",
    "find_song_info",
    "extract_info_from_endpoint",
    "search_song_data",
    "extract_user_songs",
    "extract_users",
)

T = TypeVar("T")
U = TypeVar("U")

re_link, re_size, re_name, re_author, re_attrib = (
    r"https://audio\.ngfiles\.com/([^\"']+)",
    r".filesize.:(\d+)",
    r"<title>([^<>]+)</title>",
    r".artist.:.([^\"']+).",
    r"{}[ ]*=[ ]*(?P<quote>[\"'])(.*?)(?P=quote)",
)
re_class = re_attrib.format("class")

SongInfo = namedtuple("SongInfo", "link size name author")


def html_parse(text: str) -> Element:
    text = re.sub(re_class, lambda match: match.group(0).replace(" ", ""), text)

    if use_lxml:
        return html.fromstring(text)
    else:
        return parse(text, "etree", False)


def find_song_info(text: str) -> SongInfo:
    try:
        return SongInfo(
            link=re.search(re_link, text).group(0),
            size=int(re.search(re_size, text).group(1)),
            name=re.search(re_name, text).group(1),
            author=re.search(re_author, text).group(1),
        )
    except AttributeError:  # not found
        raise ValueError("Song info was not found.") from None


def extract_info_from_endpoint(text: str) -> ExtDict:
    artist, whitelisted, scouted, song, api, *_ = filter(is_not_empty, re.split(r"</?br>", text))
    return ExtDict(
        artist=artist.split("Artist: ").pop(),
        song=song.split("Song: ").pop(),
        whitelisted=check_not(whitelisted),
        scouted=check_not(scouted),
        api=check_not(api),
    )


def search_song_data(text: str) -> List[ExtDict]:
    tree, result = html_parse(text), []

    for a, div in zip(
        tree.findall(r'.//a[@class="item-audiosubmission"]'),
        tree.findall(r'.//div[@class="detail-title"]'),
    ):
        url = URL(a.attrib["href"]).with_scheme("https")
        song_id = int(url.parts[-1])

        h4, span, *_ = div.getchildren()

        name = switch_if_none(h4.text, "") + "".join(
            switch_if_none(mark.text, "") + switch_if_none(mark.tail, "")
            for mark in h4.getchildren()
        )
        author = span.getchildren()[0].text

        result.append(ExtDict(id=song_id, name=name, author=author, links={"normal": str(url)}))

    return result


def extract_user_songs(
    json: Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]
) -> List[ExtDict]:
    result = []

    try:
        years = json["years"].values()
    except (TypeError, AttributeError):  # not found
        return result

    for entry in chain.from_iterable(year["items"] for year in years):
        tree = html_parse(entry)
        a = tree.findall(r'.//a[@class="item-link"]')[0]

        url = URL(a.attrib["href"]).with_scheme("https")
        song_id = int(url.parts[-1])

        name = a.attrib["title"]

        result.append(ExtDict(id=song_id, name=name, links={"normal": str(url)}))

    return result


def extract_users(text: str) -> List[ExtDict]:
    tree, result = html_parse(text), []

    for a in tree.findall(r'.//div[@class="item-details-main"]/h4/a'):
        url = URL(a.attrib["href"]).with_scheme("https")
        name = a.text

        result.append(ExtDict(link=url, name=name))

    return result


def switch_if_none(obj: T, to: U) -> Union[T, U]:
    if obj is None:
        return to
    return obj


def check_not(string: str) -> bool:
    return "not" not in string.casefold()


def is_not_empty(string: str) -> bool:
    return len(string) > 0
