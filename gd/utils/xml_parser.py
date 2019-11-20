from xml.etree import ElementTree

PLIST_VERSION = '1.0'
GJ_VERSION = '2.0'

class XMLConverter:
    def __init__(self, attributes: dict = None):
        if attributes is None:
            attributes = {}

        self.init_version(attributes)

    def load(self, xml):
        plist = ElementTree.fromstring(xml)

        self.init_version(plist.attrib)

        root_children = plist.getchildren().pop(0).getchildren()

        ...

    def iterate(self, elements):
        grouped = zip(elements[::2], root_children[1::2])

        ...

    def init_version(self, attrib):
        self.version, self.gjver = (
            attrib.get('version', PLIST_VERSION),
            attrib.get('gjver', GJ_VERSION)
        )    

    def dump(self):
        pass
