from pathlib import Path

try:
    from lxml import etree as xml  # type: ignore
except ImportError:
    from xml.etree import ElementTree as xml

from gd.typing import Any, AnyStr, Dict, IO, TypeVar, Union
from gd.errors import XMLError

__all__ = ("XMLParser", "xml")

T = TypeVar("T")

XML_CHAR_REF_REPLACE = "xmlcharrefreplace"
XML_ENCODING = "utf-8"

PLIST_VERSION = "1.0"
GJ_VERSION = "2.0"

DECLARATION = '<?xml version="1.0"?>'
DECLARATION_BYTES = DECLARATION.encode(XML_ENCODING)

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

SKIP = {False, None}
TYPES = {float: "r", int: "i", str: "s"}


class XMLParser:
    def __init__(self, use_plist: bool = True) -> None:
        self._attrib = {"version": PLIST_VERSION, "gjver": GJ_VERSION}
        self._use_plist = use_plist

    def load_file(
        self, file_or_path: Union[IO, Path, str], encoding: str = XML_ENCODING,
    ) -> Dict[str, T]:
        try:
            return self._load(xml.parse(file_or_path, encoding=encoding))

        except Exception as error:  # noqa
            raise XMLError("Failed to parse XML file.") from error

    def load(self, xml_string: AnyStr) -> Dict[str, T]:
        try:
            return self._load(xml.fromstring(xml_string))

        except Exception as error:  # noqa
            raise XMLError("Failed to parse XML string.") from error

    def dump_file(
        self,
        some_dict: Dict[str, T],
        file_or_path: Union[IO, Path, str],
        encoding: str = XML_ENCODING,
    ) -> None:
        file: IO

        if isinstance(file_or_path, (Path, str)):
            file = open(file_or_path, "w", encoding=encoding, errors=XML_CHAR_REF_REPLACE)
            close = True

        else:
            file = file_or_path
            close = False

        try:
            file.write(DECLARATION)  # type: ignore
        except Exception:  # noqa
            try:
                file.write(DECLARATION.encode(encoding=encoding))  # type: ignore
            except Exception:  # noqa
                pass

        if close:
            file.close()

        xml.ElementTree(self._dump(some_dict)).write(file_or_path, encoding=encoding)

    def dump(self, some_dict: Dict[str, T]) -> bytes:
        return DECLARATION_BYTES + xml.tostring(self._dump(some_dict))

    def dump_string(self, some_dict: Dict[str, T], encoding: str = XML_ENCODING) -> str:
        return DECLARATION + xml.tostring(self._dump(some_dict)).decode(
            encoding=encoding, errors=XML_CHAR_REF_REPLACE
        )

    def _load(self, root: xml.Element) -> Dict[str, T]:
        if root.tag == "plist":
            try:
                root = root[0]
                self._attrib.update(root.attrib)
            except IndexError:
                return {}

        return self.iterate_xml(root)

    def _dump(self, some_dict: Dict[str, T]) -> xml.Element:
        if self._use_plist:
            root = xml.Element("plist", attrib=self._attrib)
            element = xml.SubElement(root, "dict")
        else:
            element = root = xml.Element("dict")

        self.iterate_dict(element, some_dict)

        return root

    def iterate_xml(self, element: xml.Element) -> Dict[str, T]:
        element_it = iter(element)

        groups = zip(element_it, element_it)

        return {key.text: _process(self, inner.tag, inner) for key, inner in groups}

    def iterate_dict(self, element: xml.Element, some_dict: Dict[str, T]) -> None:
        for key, value in some_dict.items():
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
                    value = int(value)  # type: ignore

                sub.text = str(value)


def _bool(parser: XMLParser, element: xml.Element) -> bool:
    # accepts either "t" or "f"
    return element.tag == "t"


def _int(parser: XMLParser, element: xml.Element) -> int:
    return int(element.text)


def _real(parser: XMLParser, element: xml.Element) -> float:
    return float(element.text)


def _str(parser: XMLParser, element: xml.Element) -> str:
    return element.text


def _recurse(parser: XMLParser, element: xml.Element) -> Dict[str, T]:
    return parser.iterate_xml(element)


DEFAULT = _str
FUNCTIONS = {"d": _recurse, "f": _bool, "i": _int, "r": _real, "s": _str, "t": _bool}
FUNCTIONS.update({SHORT_TO_LONG_NAME[short_name]: func for short_name, func in FUNCTIONS.items()})


def _process(parser: XMLParser, tag: str, element: xml.Element) -> Any:
    return FUNCTIONS.get(tag, DEFAULT)(parser, element)
