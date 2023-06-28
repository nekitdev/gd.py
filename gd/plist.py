from typing import Dict, List, Optional, Tuple

try:
    from lxml import etree as xml

    Element = xml._Element

except ImportError:
    from xml.etree import ElementTree as xml  # type: ignore

    Element = xml.Element  # type: ignore

from attrs import define, field
from funcs.unpacking import unpack_binary
from iters.iters import iter
from named import get_type_name
from typing_aliases import Attributes, StringDict, Unary, is_instance
from typing_extensions import Literal

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.models_utils import float_str
from gd.string_utils import tick
from gd.typing import AnyString, StrictPayload

__all__ = ("PARSER", "PropertyList")

XML_CHAR_REF_REPLACE = "xmlcharrefreplace"

GD_VERSION = "2.0"
PLIST_VERSION = "1.0"
XML_VERSION = "1.0"

PLIST_VERSION_LITERAL = "version"
GD_VERSION_LITERAL = "gjver"

DECLARATION_STRING = f"""
<?xml version="{XML_VERSION}"?>
""".strip()
DECLARATION = DECLARATION_STRING.encode(DEFAULT_ENCODING, DEFAULT_ERRORS)

PLIST = "plist"

create_element = xml.Element
create_sub_element = xml.SubElement

DEFAULT_PLIST = False

DEFAULT_IGNORE_FALSY = True
DEFAULT_SHORT = True
DEFAULT_FIRST_SHOT = True
NOT_FIRST_SHOT = False


from_string = xml.fromstring
to_string = xml.tostring


def attributes_factory() -> Attributes:
    return {PLIST_VERSION_LITERAL: PLIST_VERSION, GD_VERSION_LITERAL: GD_VERSION}


DICT = "dict"
KEY = "key"
ARRAY = "array"
STRING = "string"
INT = "integer"
FLOAT = "real"
TRUE = "true"
FALSE = "false"

DICT_SHORT = "d"
KEY_SHORT = "k"
ARRAY_SHORT = "a"
STRING_SHORT = "s"
INT_SHORT = "i"
FLOAT_SHORT = "r"
TRUE_SHORT = "t"
FALSE_SHORT = "f"

EXPECTED = """
expected primitive (`bool`, `int`, `float`, `str`), primitive `list` or string `dict`, got {}
""".strip()


@define()
class PropertyList:
    attributes: Attributes = field(factory=attributes_factory, repr=False)

    def load(self, string: AnyString) -> Optional[StrictPayload]:
        plist = from_string(string)

        element = iter(plist).first().extract()

        if element is None:
            return None

        return self.load_item(element)

    def dump(
        self,
        item: Optional[StrictPayload],
        *,
        ignore_falsy: bool = DEFAULT_IGNORE_FALSY,
        short: bool = DEFAULT_SHORT,
    ) -> bytes:
        plist = create_element(PLIST, attrib=self.attributes)

        self.dump_item(item, plist, ignore_falsy=ignore_falsy, short=short)

        return DECLARATION + to_string(plist)

    def dump_string(
        self,
        item: Optional[StrictPayload],
        *,
        encoding: str = DEFAULT_ENCODING,
        ignore_falsy: bool = DEFAULT_IGNORE_FALSY,
        short: bool = DEFAULT_SHORT,
    ) -> str:
        return self.dump(item, ignore_falsy=ignore_falsy, short=short).decode(
            encoding, XML_CHAR_REF_REPLACE
        )

    def dump_item(
        self,
        item: Optional[StrictPayload],
        root: Optional[Element] = None,
        *,
        ignore_falsy: bool = DEFAULT_IGNORE_FALSY,
        short: bool = DEFAULT_SHORT,
    ) -> Optional[Element]:
        return (
            self.dump_item_short(item, root, ignore_falsy=ignore_falsy)
            if short
            else self.dump_item_long(item, root, ignore_falsy=ignore_falsy)
        )

    def dump_item_long(
        self,
        item: Optional[StrictPayload],
        root: Optional[Element] = None,
        *,
        ignore_falsy: bool = DEFAULT_IGNORE_FALSY,
    ) -> Optional[Element]:
        if item is None:
            return None

        if not item and ignore_falsy:
            return None

        if is_instance(item, str):
            element = create_element(STRING)
            element.text = item

        elif is_instance(item, float):
            element = create_element(FLOAT)
            element.text = float_str(item)

        elif item is True:
            element = create_element(TRUE)

        elif item is False:
            element = create_element(FALSE)

        elif is_instance(item, int):
            element = create_element(INT)
            element.text = str(item)

        elif is_instance(item, Dict):
            element = create_element(DICT)

            for sub_key, sub_item in item.items():
                key_element = create_sub_element(element, KEY)
                key_element.text = sub_key

                sub_element = self.dump_item_long(sub_item, element)

                if sub_element is None:
                    element.remove(key_element)

        elif is_instance(item, List):
            element = create_element(ARRAY)

            for sub_item in item:
                self.dump_item_long(sub_item, element)

        else:
            raise ValueError(EXPECTED.format(tick(get_type_name(item))))

        if root is not None:
            root.append(element)

        return element

    def dump_item_short(
        self,
        item: Optional[StrictPayload],
        root: Optional[Element] = None,
        *,
        first_shot: bool = DEFAULT_FIRST_SHOT,
        ignore_falsy: bool = DEFAULT_IGNORE_FALSY,
    ) -> Optional[Element]:
        if item is None:
            return None

        if not item and ignore_falsy:
            return None

        if is_instance(item, str):
            element = create_element(STRING_SHORT)
            element.text = item

        elif is_instance(item, float):
            element = create_element(FLOAT_SHORT)
            element.text = float_str(item)

        elif item is True:
            element = create_element(TRUE_SHORT)

        elif item is False:
            element = create_element(FALSE_SHORT)

        elif is_instance(item, int):
            element = create_element(INT_SHORT)
            element.text = str(item)

        elif is_instance(item, Dict):
            element = create_element(DICT if first_shot else DICT_SHORT)

            for sub_key, sub_item in item.items():
                key_element = create_sub_element(element, KEY_SHORT)
                key_element.text = sub_key

                sub_element = self.dump_item_short(sub_item, element, first_shot=NOT_FIRST_SHOT)

                if sub_element is None:
                    element.remove(key_element)

        elif is_instance(item, List):
            element = create_element(ARRAY_SHORT)

            for sub_item in item:
                self.dump_item_short(sub_item, element, first_shot=False)

        else:
            raise ValueError(EXPECTED.format(tick(get_type_name(item))))

        if root is not None:
            root.append(element)

        return element

    @staticmethod
    def load_item(element: Element) -> StrictPayload:
        return LOAD[element.tag](element)


PARSER = PropertyList()  # the parser is stateless, so it can be reused


load_item = PropertyList.load_item


DEFAULT_STRING = str()
DEFAULT_FLOAT = 0.0
DEFAULT_INT = 0


def load_array(elements: Element) -> List[StrictPayload]:
    return iter(elements).map(load_item).list()


StringEntry = Tuple[str, StrictPayload]


def load_entry(key: Element, item: Element) -> StringEntry:
    return load_string(key), load_item(item)


def load_dict(elements: Element) -> StringDict[StrictPayload]:
    return iter(elements).pairs().map(unpack_binary(load_entry)).dict()


def load_false(element: Element) -> Literal[False]:
    return False


def load_true(element: Element) -> Literal[True]:
    return True


def load_float(element: Element) -> float:
    string = element.text

    return DEFAULT_FLOAT if string is None else float(string)


def load_int(element: Element) -> int:
    string = element.text

    return DEFAULT_INT if string is None else int(string)


def load_string(element: Element) -> str:
    string = element.text

    return DEFAULT_STRING if string is None else string


Load = Unary[Element, StrictPayload]

LOAD: StringDict[Load] = {
    ARRAY_SHORT: load_array,
    ARRAY: load_array,
    DICT_SHORT: load_dict,
    DICT: load_dict,
    KEY: load_string,
    KEY_SHORT: load_string,
    FALSE_SHORT: load_float,
    FALSE: load_float,
    INT_SHORT: load_int,
    INT: load_int,
    FLOAT_SHORT: load_float,
    FLOAT: load_float,
    STRING_SHORT: load_string,
    STRING: load_string,
    TRUE_SHORT: load_true,
    TRUE: load_true,
}
