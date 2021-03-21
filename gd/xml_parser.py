try:
    from lxml import etree as xml  # type: ignore
except ImportError:
    from xml.etree import ElementTree as xml

from gd.iter_utils import mapping_merge
from gd.text_utils import make_repr
from gd.typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, TypeVar, Union, cast

__all__ = ("NoDefault", "NoDefaultOr", "XMLParser", "no_default")

T = TypeVar("T")


class NoDefault:
    pass


AnyString = Union[bytes, str]

NoDefaultOr = Union[NoDefault, T]

no_default = NoDefault()

XML_CHAR_REF_REPLACE = "xmlcharrefreplace"
XML_ENCODING = "utf-8"

GJ_VERSION = "2.0"
PLIST_VERSION = "1.0"
XML_VERSION = "1.0"

DECLARATION = f'<?xml version="{XML_VERSION}"?>'
DECLARATION_DATA = DECLARATION.encode(XML_ENCODING)


class XMLParser:
    PLIST_ATTRS = {"version": PLIST_VERSION, "gjver": GJ_VERSION}

    def __init__(self, plist: bool = False, **plist_attrs) -> None:
        self.plist = plist

        self.plist_attrs = mapping_merge(self.PLIST_ATTRS, plist_attrs)

    def __repr__(self) -> str:
        info = {"plist": self.plist}

        return make_repr(self, info)

    def load(self, string: AnyString, default: NoDefaultOr[T] = no_default) -> T:
        element = xml.fromstring(string)

        if element.tag == "plist":
            self.plist = True

            try:
                element = element[0]

            except IndexError:
                return cast(T, {})

        try:
            return self.parse_value(element)

        except Exception:
            if default is no_default:
                raise

            return cast(T, default)

    def dump_as_bytes(self, value: T, ignore_false: bool = True, short: bool = True) -> bytes:
        if self.plist:
            root = xml.Element("plist", attrib=self.plist_attrs)
            element = self.unparse_value(value, root, ignore_false=ignore_false, short=short)

        else:
            root = element = self.unparse_value(value, ignore_false=ignore_false, short=short)

        if element is None:
            return DECLARATION_DATA

        return DECLARATION_DATA + xml.tostring(root)

    def dump(
        self, value: T, encoding: str = XML_ENCODING, ignore_false: bool = True, short: bool = True
    ) -> str:
        return self.dump_as_bytes(value, ignore_false=ignore_false, short=short).decode(
            encoding=encoding, errors=XML_CHAR_REF_REPLACE
        )

    def unparse_value(
        self,
        value: Optional[T],
        root_element: Optional[xml.Element] = None,
        *,
        short: bool = True,
        ignore_false: bool = True,
    ) -> Optional[xml.Element]:
        return (
            self.unparse_value_short(value, root_element, ignore_false=ignore_false)
            if short
            else self.unparse_value_long(value, root_element, ignore_false=ignore_false)
        )

    def unparse_value_long(
        self,
        value: Optional[T],
        root_element: Optional[xml.Element] = None,
        *,
        ignore_false: bool = True,
    ) -> Optional[xml.Element]:
        if value is None:
            return None

        if ignore_false and value is False:
            return None

        if isinstance(value, str):
            element = xml.Element("string")
            element.text = value

        elif isinstance(value, float):
            truncated = int(value)

            element = xml.Element("real")
            element.text = str(value if truncated != value else truncated)

        elif isinstance(value, bool):
            element = xml.Element("true") if value else xml.Element("false")

        elif isinstance(value, int):
            element = xml.Element("integer")
            element.text = str(value)

        elif isinstance(value, Mapping):
            element = xml.Element("dict")

            for key, map_value in value.items():
                xml.SubElement(element, "key").text = key

                self.unparse_value_long(map_value, element)

        elif isinstance(value, Iterable):
            element = xml.Element("array")

            for item in value:
                self.unparse_value_long(item, element)

        else:
            raise ValueError(
                f"Expected mapping, iterable, bool, float, int or str, got {type(value).__name__}."
            )

        if root_element is not None:
            root_element.append(element)

        return element

    def unparse_value_short(
        self,
        value: Optional[T],
        root_element: Optional[xml.Element] = None,
        *,
        first_shot: bool = True,
        ignore_false: bool = False,
    ) -> Optional[xml.Element]:
        if value is None:
            return None

        if ignore_false and value is False:
            return None

        if isinstance(value, str):
            element = xml.Element("s")
            element.text = value

        elif isinstance(value, float):
            truncated = int(value)

            element = xml.Element("r")
            element.text = str(value if truncated != value else truncated)

        elif isinstance(value, bool):
            element = xml.Element("t") if value else xml.Element("f")

        elif isinstance(value, int):
            element = xml.Element("i")
            element.text = str(value)

        elif isinstance(value, Mapping):
            element = xml.Element("dict" if first_shot else "d")

            for key, map_value in value.items():
                xml.SubElement(element, "k").text = key

                self.unparse_value_short(map_value, element, first_shot=False)

        elif isinstance(value, Iterable):
            element = xml.Element("a")

            for item in value:
                self.unparse_value_short(item, element, first_shot=False)

        else:
            raise ValueError(
                f"Expected mapping, iterable, bool, float, int or str, got {type(value).__name__}."
            )

        if root_element is not None:
            root_element.append(element)

        return element

    @staticmethod
    def parse_value(element: xml.Element) -> T:
        return PARSE.get(element.tag, parse_str)(element)  # type: ignore


def parse_array(elements: xml.Element) -> List[T]:
    return [
        PARSE.get(element.tag, parse_str)(element) for element in elements  # type: ignore
    ]


def parse_dict(elements: xml.Element) -> Dict[str, T]:
    if not len(elements):
        return {}

    elements_iter = iter(elements)

    groups = zip(elements_iter, elements_iter)

    return {  # inline
        key.text: PARSE.get(element.tag, parse_str)(element)  # type: ignore
        for key, element in groups
    }


def parse_false(element: xml.Element) -> bool:
    return False


def parse_float(element: xml.Element) -> float:
    string = element.text

    return 0.0 if string is None else float(string)


def parse_int(element: xml.Element) -> int:
    string = element.text

    return 0 if string is None else int(string)


def parse_str(element: xml.Element) -> str:
    string = element.text

    return "" if string is None else string


def parse_true(element: xml.Element) -> bool:
    return True


PARSE: Dict[str, Callable[[xml.Element], Any]] = {
    "a": parse_array,
    "array": parse_array,
    "d": parse_dict,
    "dict": parse_dict,
    "f": parse_float,
    "false": parse_float,
    "i": parse_int,
    "integer": parse_int,
    "r": parse_float,
    "real": parse_float,
    "s": parse_str,
    "string": parse_str,
    "t": parse_true,
    "true": parse_true,
}
