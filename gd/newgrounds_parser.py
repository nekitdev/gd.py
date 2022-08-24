"""This module is used for Newgrounds parsing."""

# HTML, RE and XML parsing never looks clean... ~ nekit

import re
from itertools import chain
from xml.etree import ElementTree as xml

from typing_extensions import Final
from yarl import URL

from gd.errors import MissingAccess

Element = xml.Element

log = get_logger(__name__)

FAST = False

try:
    from lxml import html  # type: ignore

    FAST = True

    Element = html.HtmlElement  # type: ignore

except ImportError:
    try:
        from html5lib import parse  # type: ignore

    except ImportError:
        log.warning("Failed to import lxml and html5lib. Newgrounds parsing will not be supported.")


__all__ = (
    "FAST",
    "find_song_data",
    "find_info",
    "search_song_data",
    "search_user_songs",
    "search_users",
)

T = TypeVar("T")
U = TypeVar("U")

FACTOR = 1024
ROUNDING = 2


def string_to_megabytes(string: str) -> float:
    return round(int(string) / FACTOR / FACTOR, ROUNDING)


QUOTE: Final = '"'


def quote(string: str) -> str:
    quote = QUOTE

    return quote + string + quote


re_link = re.compile(r"(https://audio\.ngfiles\.com/[^\"']+)")
re_size = re.compile(r"[\"']filesize[\"'][ ]*:[ ]*(\d+)")
re_name = re.compile(r"<title>([^<>]+)</title>")
re_author = re.compile(r"[\"']artist[\"'][ ]*:[ ]*[\"']([^\"']+)[\"']")

re_patterns = {
    "download_link": (re_link, str),
    "size": (re_size, string_to_megabytes),
    "name": (re_name, str),
    "author": (re_author, str),
}

re_attrib = r"{}[ ]*=[ ]*(?P<quote>[\"'])(.*?)(?P=quote)"
re_class = re.compile(re_attrib.format("class"))

re_newline = "\n"
re_break = r"</?br>"


def negate(something: T) -> bool:
    return not something


re_info_functions = {
    "artist": (1, str),
    "whitelisted": (2, negate),
    "scouted": (3, negate),
    "song": (4, str),
    "api": (5, negate),
}

empty = ""
space = " "


def remove_spaces(match: Match[str]) -> str:
    return match.group(0).replace(space, empty)


element_tree = "etree"


def html_parse(string: str) -> Element:
    string = re_class.sub(remove_spaces, string)

    if FAST:
        return cast(Element, html.fromstring(string))

    else:
        return cast(Element, parse(string, element_tree, False))


Data = Dict[T, Union[T, U]]


def find_song_data(string: str) -> Data[str, int]:
    try:
        return {
            name: function(pattern.search(string).group(1))  # type: ignore
            for name, (pattern, function) in re_patterns.items()
        }

    except AttributeError:
        raise MissingAccess("Song info was not found.") from None


def find_info(string: str) -> Data[str, bool]:
    match = re_info.match(string)

    if match is None:
        raise MissingAccess("Artist info was not found.")

    return {
        name: function(match.group(group))  # type: ignore
        for name, (group, function) in re_info_functions.items()
    }


item_submission = r'.//a[@class="item-audiosubmission"]'
item_title = r'.//div[@class="detail-title"]'

HTTPS = "https"
HREF = "href"


def search_song_data(text: str) -> Iterator[Dict[str, Union[int, str]]]:
    tree = html_parse(text)

    for a_element, div_element in zip(tree.findall(item_submission), tree.findall(item_title)):
        url = URL(a_element.attrib[href]).with_scheme(https)

        id = int(url.name)

        element_iterator = iter(div_element)

        h4_element = next(element_iterator)
        span_element = next(element_iterator)

        name = (h4_element.text or empty) + empty.join(
            (mark_element.text or empty) + (mark_element.tail or empty)
            for mark_element in h4_element
        )

        element_iterator = iter(span_element)

        element = next(element_iterator)

        author = str(element.text)

        yield dict(id=id, name=name, author=author, link=str(url))


ITEM_LINK = "item-link"

ITEM_LINK_PATH = rf"""
.//a[@class="{ITEM_LINK}"]
""".strip()

YEARS = "years"
ITEMS = "items"
TITLE = "title"


def search_user_songs(
    json: Namespace,
    # {
    #     years: {
    #         year: {
    #             items: [entry, ...]
    #         },
    #         ...
    #     },
    #     showcase: {...}  // do not care about this
    # }
) -> Iterator[Data[str, int]]:
    for entry in chain.from_iterable(year[items] for year in json[years].values()):
        tree = html_parse(entry)

        element_iterator = iter(tree.findall(item_link))

        a_element = next(element_iterator)

        url = URL(a_element.attrib[href]).with_scheme(https)

        id = int(url.name)

        name = str(a_element.attrib[title])

        yield dict(id=id, name=name, link=str(url))


item_details = r'.//div[@class="item-details-main"]/h4/a'


def search_users(text: str) -> Iterator[Data[str, str]]:
    tree = html_parse(text)

    for a_element in tree.findall(item_details):
        url = URL(a_element.attrib[href]).with_scheme(https)

        name = str(a_element.text)

        yield dict(name=name, link=str(url))


@overload
def check_none(some: Literal[None], other: U) -> U:
    ...


@overload
def check_none(some: T, other: U) -> T:
    ...


def check_none(some: Optional[T], other: U) -> Union[T, U]:
    return other if some is None else some
