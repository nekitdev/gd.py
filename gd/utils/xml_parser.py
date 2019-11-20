import xml.etree.ElementTree as xml

from ._async import run_blocking_io

PLIST_VERSION = '1.0'
GJ_VERSION = '2.0'
DECLARATION = '<?xml version="1.0"?>'


class XMLParser:
    def __init__(self):
        self._default({})

    def load(self, xml_string):
        plist = xml.fromstring(xml_string)

        self._default(plist.attrib)

        root = plist.getchildren().pop(0)

        return self.iterate_xml(root)

    def iterate_xml(self, element):
        elements = element.getchildren()
        grouped = zip(elements[::2], elements[1::2])

        ret = {}

        for key, inner in grouped:

            if inner.tag == 'd':
                ret[key.text] = self.iterate_xml(inner)

            elif inner.tag in ('f', 't'):
                ret[key.text] = (inner.tag == 't')

            else:
                func = {'i': int, 'r': float, 's': str}.get(inner.tag)
                ret[key.text] = func(inner.text)

        return ret

    def dump(self, py_dict):
        plist = xml.Element('plist', attrib=self.attrib)
        root = xml.SubElement(plist, 'dict')

        self.iterate_dict(root, py_dict)

        return self._dump(plist)
        
    def iterate_dict(self, element, py_dict):
        for key, value in py_dict.items():
            k = xml.SubElement(element, 'k')
            k.text = key

            if isinstance(value, dict):
                sub = xml.SubElement(element, 'd')
                self.iterate_dict(sub, value)

            elif isinstance(value, bool):
                tag = {0: 'f', 1: 't'}.get(value)
                xml.SubElement(element, tag)

            else:
                tag = {int: 'i', float: 'r', str: 's'}.get(type(value))
                sub = xml.SubElement(element, tag)

                if isinstance(value, float) and value.is_integer():
                    value = round(value)

                sub.text = str(value)

    def _dump(self, element):
        return DECLARATION + xml.tostring(element).decode(errors='replace').replace('!version', 'version', 1)

    def _default(self, _dict):
        self.attrib = {
            '!version': _dict.get('version', PLIST_VERSION),
            'gjver': _dict.get('gjver', GJ_VERSION)
        }


class AioXMLParser(XMLParser):
    async def load(self, xml_string):
        return await run_blocking_io(super().load, xml_string)

    async def dump(self, py_dict):
        return await run_blocking_io(super().dump, py_dict)
