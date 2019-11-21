from collections import namedtuple

from .xml_parser import XMLParser, AioXMLParser

Save = namedtuple('Save', 'completed followed')


class SaveParser:
    @staticmethod
    def parse(xml):
        parser = XMLParser()
        _dict = parser.load(xml)

        return SaveParser._parse(_dict)

    @staticmethod
    async def aio_parse(xml):
        parser = AioXMLParser()
        _dict = await parser.load(xml)

        return SaveParser._parse(_dict)

    @staticmethod
    def _parse(d):
        completed = _get_completed(d)
        followed = _get_followed(d)

        return Save(completed=completed, followed=followed)


def _get_completed(d):
    inner = d['GS_completed']

    final = []

    for entry, _ in inner.items():

        if entry.startswith('c_'):
            _id = int(entry.lstrip('c_'))

            final.append(_id)

    return final

def _get_followed(d):
    inner = d['GLM_06']

    final = [
        int(entry) for entry, _ in inner.items()
    ]

    return final
