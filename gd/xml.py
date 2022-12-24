from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, TypeVar, Union

try:
    from lxml import etree as xml

    Element = xml._Element

except ImportError:
    from xml.etree import ElementTree as xml  # type: ignore

    Element = xml.Element  # type: ignore

from attrs import define, field
from iters import iter
from named import get_type_name
from solus import Singleton

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.models_utils import float_str
from gd.string_utils import tick
from gd.typing import AnyString, Unary, is_instance

__all__ = ("PARSER", "XML")

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

DEFAULT_IGNORE_FALSE = True
DEFAULT_SHORT = True
DEFAULT_FIRST_SHOT = True
NOT_FIRST_SHOT = False


class NoDefault(Singleton):
    pass


no_default = NoDefault()

T = TypeVar("T")

NoDefaultOr = Union[NoDefault, T]


from_string = xml.fromstring
to_string = xml.tostring


def plist_attrs_factory() -> Dict[str, Any]:
    return {PLIST_VERSION_LITERAL: PLIST_VERSION, GD_VERSION_LITERAL: GD_VERSION}


FIRST = 0


def first(sequence: Sequence[T]) -> T:
    return sequence[FIRST]


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

EXPECTED = "expected int, float, str, bool, mapping or iterable, got {}"


@define()
class XML:
    plist: bool = field(default=DEFAULT_PLIST)
    plist_attrs: Dict[str, Any] = field(factory=plist_attrs_factory, repr=False)

    def load(self, string: AnyString, default: NoDefaultOr[Any] = no_default) -> Any:
        element = from_string(string)

        if element.tag == PLIST:
            self.plist = True

            try:
                element = first(element)  # type: ignore

            except IndexError:
                return {}

        try:
            return self.load_value(element)

        except Exception:
            if default is no_default:
                raise

            return default

    def dump(
        self,
        value: Any,
        *,
        ignore_false: bool = DEFAULT_IGNORE_FALSE,
        short: bool = DEFAULT_SHORT,
    ) -> bytes:
        if self.plist:
            root = create_element(PLIST, attrib=self.plist_attrs)

            element = self.dump_value(value, root, ignore_false=ignore_false, short=short)

        else:
            root = element = self.dump_value(  # type: ignore
                value, ignore_false=ignore_false, short=short
            )

        if element is None:
            return DECLARATION

        return DECLARATION + to_string(root)

    def dump_string(
        self,
        value: Any,
        *,
        encoding: str = DEFAULT_ENCODING,
        ignore_false: bool = DEFAULT_IGNORE_FALSE,
        short: bool = DEFAULT_SHORT,
    ) -> str:
        return self.dump(value, ignore_false=ignore_false, short=short).decode(
            encoding, XML_CHAR_REF_REPLACE
        )

    def dump_value(
        self,
        value: Optional[Any],
        root: Optional[Element] = None,
        *,
        ignore_false: bool = DEFAULT_IGNORE_FALSE,
        short: bool = DEFAULT_SHORT,
    ) -> Optional[Element]:
        return (
            self.dump_value_short(value, root, ignore_false=ignore_false)
            if short
            else self.dump_value_long(value, root, ignore_false=ignore_false)
        )

    def dump_value_long(
        self,
        value: Optional[Any],
        root: Optional[Element] = None,
        *,
        ignore_false: bool = DEFAULT_IGNORE_FALSE,
    ) -> Optional[Element]:
        if value is None:
            return None

        if ignore_false and value is False:
            return None

        if is_instance(value, str):
            element = create_element(STRING)
            element.text = value

        elif is_instance(value, float):
            element = create_element(FLOAT)
            element.text = float_str(value)

        elif value is True:
            element = create_element(TRUE)

        elif value is False:
            element = create_element(FALSE)

        elif is_instance(value, int):
            element = create_element(INT)
            element.text = str(value)

        elif is_instance(value, Mapping):
            element = create_element(DICT)

            for sub_key, sub_value in value.items():
                sub_element = create_sub_element(element, KEY)
                sub_element.text = sub_key

                self.dump_value_long(sub_value, element)

        elif is_instance(value, Iterable):
            element = create_element(ARRAY)

            for item in value:
                self.dump_value_long(item, element)

        else:
            raise ValueError(EXPECTED.format(tick(get_type_name(value))))

        if root is not None:
            root.append(element)

        return element

    def dump_value_short(
        self,
        value: Optional[Any],
        root: Optional[Element] = None,
        *,
        first_shot: bool = DEFAULT_FIRST_SHOT,
        ignore_false: bool = DEFAULT_IGNORE_FALSE,
    ) -> Optional[Element]:
        if value is None:
            return None

        if ignore_false and value is False:
            return None

        if is_instance(value, str):
            element = create_element(STRING_SHORT)
            element.text = value

        elif is_instance(value, float):
            element = create_element(FLOAT_SHORT)
            element.text = float_str(value)

        elif value is True:
            element = create_element(TRUE_SHORT)

        elif value is False:
            element = create_element(FALSE_SHORT)

        elif is_instance(value, int):
            element = create_element(INT_SHORT)
            element.text = str(value)

        elif is_instance(value, Mapping):
            element = create_element(DICT if first_shot else DICT_SHORT)

            for sub_key, sub_value in value.items():
                sub_element = create_sub_element(element, KEY_SHORT)
                sub_element.text = sub_key

                self.dump_value_short(sub_value, element, first_shot=NOT_FIRST_SHOT)

        elif is_instance(value, Iterable):
            element = create_element(ARRAY_SHORT)

            for sub_value in value:
                self.dump_value_short(sub_value, element, first_shot=False)

        else:
            raise ValueError(EXPECTED.format(tick(get_type_name(value))))

        if root is not None:
            root.append(element)

        return element

    @staticmethod
    def load_value(element: Element) -> Any:  # type: ignore
        return LOAD.get(element.tag, load_string)(element)


PARSER = XML()  # the parser is essentially stateless, so it can be reused


load_value = XML.load_value


DEFAULT_STRING = str()
DEFAULT_FLOAT = 0.0
DEFAULT_INT = 0


def load_array(elements: Element) -> List[Any]:
    return iter(elements).map(load_value).list()


def load_dict(elements: Element) -> Dict[str, Any]:
    return iter(elements).map(load_value).pairs().dict()


def load_false(element: Element) -> bool:
    return False


def load_true(element: Element) -> bool:
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


LOAD: Dict[str, Unary[Element, Any]] = {
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
