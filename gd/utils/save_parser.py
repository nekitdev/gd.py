from collections import namedtuple
import re

Save = namedtuple('Save', 'completed followed')

class SaveParser:
    @classmethod
    def parse(cls, xml):
        completed = cls.parse_completed_levels(xml)
        followed = cls.parse_followed(xml)
        return Save(completed=completed, followed=followed)

    @classmethod
    def parse_completed_levels(cls, xml):
        pattern = '<k>c_(\d+)</k><s>1</s>'
        found = re.findall(pattern, xml)

        return list(map(int, found))

    @classmethod
    def parse_followed(cls, xml):
        try:
            section = _slice_between(xml, 'GLM', 6, 8)
        except Exception:
            section = _slice_between(xml, 'GLM', 6, 7)

        pattern = '<k>(\d+)</k><s>1</s>'
        found = re.findall(pattern, section)

        return list(map(int, found))

def _slice_between(sequence, section_name, x, y):
    fix = len(section_name) + 3

    x, y = ('{}_{:02}'.format(section_name, z) for z in (x, y))
    i, j = (sequence.index(z) for z in (x, y))
    i += fix

    return sequence[i:j]
