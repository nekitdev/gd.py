from collections import namedtuple
import re

# more things soon <3

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
        found = re.findall(pattern.encode(), xml)

        return map_to_int(found)

    @classmethod
    def parse_followed(cls, xml):
        try:
            section = slice_between(xml, 'GLM', 6, 8)
        except Exception:
            section = slice_between(xml, 'GLM', 6, 7)

        pattern = '<k>(\d+)</k><s>1</s>'
        found = re.findall(pattern.encode(), section)

        return map_to_int(found)

def map_to_int(seq):
    return [int(x) for x in seq]

def slice_between(sequence, section_name, x, y):
    fix = len(section_name) + 3

    x, y = (f'{section_name}_{z:02}' for z in (x, y))
    i, j = (sequence.index(z.encode()) for z in (x, y))
    i += fix

    return sequence[i:j]