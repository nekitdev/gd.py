try:
    from lxml import etree as xml
except ImportError:
    from xml.etree import ElementTree as xml

from gd.utils.async_utils import run_blocking_io

from gd.typing import Any, Dict, Union
from gd.errors import ParserError

__all__ = ("xml", "XMLParser", "AioXMLParser")

PLIST_VERSION = "1.0"
GJ_VERSION = "2.0"
DECLARATION = '<?xml version="1.0"?>'
LONG_TO_SHORT_NAME = {
    "dict": "d",
    "key": "k",
    "true": "t",
    "false": "f",
    "integer": "i",
    "real": "r",
    "string": "s",
}
SHORT_TO_LONG_NAME = {value: key for key, value in LONG_TO_SHORT_NAME.items()}
TYPES = {float: "r", int: "i", str: "s"}


class XMLParser:
    def __init__(self) -> None:
        self._default({})

    def load(self, xml_string: Union[bytes, str]) -> Dict[str, Any]:
        try:
            plist = xml.fromstring(xml_string)

            self._default(plist.attrib)

            root = list(plist).pop(0)

            return self.iterate_xml(root)

        except Exception as exc:
            raise ParserError("Failed to parse xml string.") from exc

    def iterate_xml(self, element: xml.Element) -> Dict[str, Any]:
        element_it = iter(element)
        groups = zip(element_it, element_it)

        return {key.text: _process(self, inner.tag, inner) for key, inner in groups}

    def dump(self, py_dict: Dict[str, Any]) -> str:
        plist = xml.Element("plist", attrib=self.attrib)
        root = xml.SubElement(plist, "dict")

        self.iterate_dict(root, py_dict)

        return self._dump(plist)

    def iterate_dict(self, element: xml.Element, py_dict: Dict[str, Any]) -> None:
        for key, value in py_dict.items():
            if value is None or value is False:  # exactly bool here
                continue

            k = xml.SubElement(element, "k")
            k.text = key

            if isinstance(value, dict):
                sub = xml.SubElement(element, "d")
                self.iterate_dict(sub, value)

            elif value is True:
                xml.SubElement(element, "t")

            else:
                sub = xml.SubElement(element, TYPES.get(type(value), "s"))

                if isinstance(value, float) and value.is_integer():
                    value = int(value)

                sub.text = str(value)

    def _dump(self, element: xml.Element) -> str:
        string = xml.tostring(element).decode(errors="replace")
        return DECLARATION + string

    def _default(self, _dict: Dict[str, str]) -> None:
        self.attrib = {
            "version": _dict.get("version", PLIST_VERSION),
            "gjver": _dict.get("gjver", GJ_VERSION),
        }


class AioXMLParser(XMLParser):
    async def load(self, xml_string: str) -> Dict[str, Any]:
        return await run_blocking_io(super().load, xml_string)

    async def dump(self, py_dict: Dict[str, Any]) -> str:
        return await run_blocking_io(super().dump, py_dict)


def _bool(parser: XMLParser, element: xml.Element) -> bool:
    # accepts either "t" or "f"
    return element.tag == "t"


def _int(parser: XMLParser, element: xml.Element) -> int:
    return int(element.text)


def _real(parser: XMLParser, element: xml.Element) -> float:
    return float(element.text)


def _str(parser: XMLParser, element: xml.Element) -> str:
    return element.text


def _recurse(parser: XMLParser, element: xml.Element) -> Any:
    return parser.iterate_xml(element)


DEFAULT = _str
FUNCTIONS = {"d": _recurse, "f": _bool, "i": _int, "r": _real, "s": _str, "t": _bool}
FUNCTIONS.update({SHORT_TO_LONG_NAME[short_name]: func for short_name, func in FUNCTIONS.items()})


def _process(parser: XMLParser, tag: str, element: xml.Element) -> Any:
    return FUNCTIONS.get(tag, DEFAULT)(parser, element)
