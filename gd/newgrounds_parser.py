"""This module is used for Newgrounds parsing."""

# HTML, RE and XML parsing never looks clean... ~ nekit

import re
from itertools import chain
from xml.etree.ElementTree import Element

from yarl import URL

from gd.errors import MissingAccess
from gd.logging import get_logger
from gd.typing import Dict, Generator, List, Match, Optional, TypeVar, Union

log = get_logger(__name__)

use_lxml = False

try:
    from lxml import html  # type: ignore

    use_lxml = True
    Element = html.HtmlElement  # type: ignore  # noqa

except ImportError:
    try:
        from html5lib import parse  # type: ignore

    except ImportError:
        log.warning("Failed to import lxml and html5lib. Newgrounds parsing will not be supported.")

__all__ = (
    "find_song_info",
    "extract_info_from_endpoint",
    "search_song_data",
    "extract_user_songs",
    "extract_users",
)

T = TypeVar("T")
U = TypeVar("U")


def str_bytes_to_megabytes(string: str) -> float:
    return round(int(string) / 1024 / 1024, 2)


re_link = re.compile(r"(https://audio\.ngfiles\.com/[^\"']+)")
re_size = re.compile(r"[\"']filesize[\"'][ ]*:[ ]*(\d+)")
re_name = re.compile(r"<title>([^<>]+)</title>")
re_author = re.compile(r"[\"']artist[\"'][ ]*:[ ]*[\"']([^\"']+)[\"']")

re_patterns = {
    "download_link": (re_link, str),
    "size": (re_size, str_bytes_to_megabytes),
    "name": (re_name, str),
    "author": (re_author, str),
}

re_attrib = r"{}[ ]*=[ ]*(?P<quote>[\"'])(.*?)(?P=quote)"
re_class = re.compile(re_attrib.format("class"))

re_info = re.compile(
    r"""
Artist: (.*?)
Artist is ?(NOT)? Whitelisted\.
Artist is ?(NOT)? Scouted\.

Song: (.*?)
External API ?(NOT)? allowed\.
""".strip().replace(
        "\n", r"<\/?br>"
    )
)


def negate(something: T) -> bool:
    return not something


re_info_functions = {
    "artist": (1, str),
    "whitelisted": (2, negate),
    "scouted": (3, negate),
    "song": (4, str),
    "api": (5, negate),
}


def remove_spaces(match: Match) -> str:
    return match.group(0).replace(" ", "")


def html_parse(text: str) -> Element:
    text = re_class.sub(remove_spaces, text)

    if use_lxml:
        return html.fromstring(text)

    else:
        return parse(text, "etree", False)


def find_song_info(text: str) -> Dict[str, Union[int, str]]:
    try:
        return {
            name: function(pattern.search(text).group(1))  # type: ignore
            for name, (pattern, function) in re_patterns.items()
        }

    except AttributeError:
        raise MissingAccess("Song info was not found.") from None


def extract_info_from_endpoint(text: str) -> Dict[str, Union[bool, str]]:
    match = re_info.match(text)

    if match is None:
        raise MissingAccess("Artist info was not found.")

    return {
        name: function(match.group(group))  # type: ignore
        for name, (group, function) in re_info_functions.items()
    }


def search_song_data(text: str) -> Generator[Dict[str, Union[int, str]], None, None]:
    tree = html_parse(text)

    for a_element, div_element in zip(
        tree.findall(r'.//a[@class="item-audiosubmission"]'),
        tree.findall(r'.//div[@class="detail-title"]'),
    ):
        url = URL(a_element.attrib["href"]).with_scheme("https")

        song_id = int(url.parts[-1])

        h4_element, span_element, *_ = div_element

        name = switch_if_none(h4_element.text, "") + "".join(
            switch_if_none(mark_element.text, "") + switch_if_none(mark_element.tail, "")
            for mark_element in h4_element
        )
        author = str(span_element[0].text)

        yield {"id": song_id, "name": name, "author": author, "link": str(url)}


def extract_user_songs(
    json: Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]
) -> Generator[Dict[str, Union[int, str]], None, None]:
    try:
        years = json["years"].values()

    except (AttributeError, KeyError):
        return

    for entry in chain.from_iterable(year["items"] for year in years):
        tree = html_parse(entry)

        a_element = tree.findall(r'.//a[@class="item-link"]')[0]

        url = URL(a_element.attrib["href"]).with_scheme("https")

        song_id = int(url.parts[-1])
        name = str(a_element.attrib["title"])

        yield {"id": song_id, "name": name, "link": str(url)}


def extract_users(text: str) -> Generator[Dict[str, str], None, None]:
    tree = html_parse(text)

    for a_element in tree.findall(r'.//div[@class="item-details-main"]/h4/a'):
        url = URL(a_element.attrib["href"]).with_scheme("https")
        name = str(a_element.text)

        yield {"name": name, "link": str(url)}


def switch_if_none(some: Optional[T], other: U) -> Union[T, U]:
    return other if some is None else some
