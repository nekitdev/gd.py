import xml.etree.ElementTree as xml
import re

from ._async import run_blocking_io

from .._typing import Any, Dict
from ..errors import ParserError

__all__ = ('xml', 'XMLParser', 'AioXMLParser')

PLIST_VERSION = '1.0'
GJ_VERSION = '2.0'
DECLARATION = '<?xml version="1.0"?>'
MAPPING = {
    'dict': 'd',
    'key': 'k',
    'true': 't',
    'false': 'f',
    'integer': 'i',
    'real': 'r',
    'string': 's'
}


class XMLParser:
    def __init__(self) -> None:
        self._default({})

    def preprocess(self, string: str) -> str:
        for key, value in MAPPING.items():
            string = string.replace(key, value)
        string = re.sub(r'[\n\t]', '', string)
        return string

    def load(self, xml_string: str) -> Dict[str, Any]:
        xml_string = self.preprocess(xml_string)
        try:
            plist = xml.fromstring(xml_string)

            self._default(plist.attrib)

            root = list(plist).pop(0)

            return self.iterate_xml(root)

        except Exception as exc:
            raise ParserError('Failed to parse xml string.') from exc

    def iterate_xml(self, element: xml.Element) -> Dict[str, Any]:
        elements = list(element)
        grouped = zip(elements[::2], elements[1::2])

        ret = {}

        for key, inner in grouped:

            if inner.tag == 'd':
                ret[key.text] = self.iterate_xml(inner)

            elif inner.tag in ('f', 't'):
                # well, 'f' is not used, but just in case '-')/
                ret[key.text] = (inner.tag == 't')

            else:
                func = {'i': int, 'r': float, 's': str}.get(inner.tag, str)
                ret[key.text] = func(inner.text)

        return ret

    def dump(self, py_dict: Dict[str, Any]) -> str:
        plist = xml.Element('plist', attrib=self.attrib)
        root = xml.SubElement(plist, 'dict')

        self.iterate_dict(root, py_dict)

        return self._dump(plist)

    def iterate_dict(self, element: xml.Element, py_dict: Dict[str, Any]) -> None:
        for key, value in py_dict.items():
            if value is None or value is False:  # exactly bool here
                continue

            k = xml.SubElement(element, 'k')
            k.text = key

            if isinstance(value, dict):
                sub = xml.SubElement(element, 'd')
                self.iterate_dict(sub, value)

            elif isinstance(value, bool):
                # if false -> do not add (though, this can not really happen, but anyways)
                if value:
                    xml.SubElement(element, 't')

            else:
                tag = {int: 'i', float: 'r', str: 's'}.get(type(value), 's')
                sub = xml.SubElement(element, tag)

                if isinstance(value, float) and value.is_integer():
                    value = round(value)

                sub.text = str(value)

    def _dump(self, element: xml.Element) -> str:
        string = xml.tostring(element).decode(errors='replace').replace('!version', 'version', 1)
        return DECLARATION + string

    def _default(self, _dict: Dict[str, str]) -> None:
        self.attrib = {
            '!version': _dict.get('version', PLIST_VERSION),
            'gjver': _dict.get('gjver', GJ_VERSION)
        }


class AioXMLParser(XMLParser):
    async def load(self, xml_string: str) -> Dict[str, Any]:
        return await run_blocking_io(super().load, xml_string)

    async def dump(self, py_dict: Dict[str, Any]) -> str:
        return await run_blocking_io(super().dump, py_dict)
