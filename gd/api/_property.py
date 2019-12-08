from .enums import *

__all__ = ('_template', '_create', '_object_code', '_color_code')


_template = """
@property
def {name}(self):
    return self.data.get({enum})
@{name}.setter
def {name}(self, value):
    self.data[{enum}] = value
""".strip('\n')

_properties = "existing_properties = {}"


def _create(enum):
    final = []

    for name, value in enum.as_dict().items():
        final.append(_template.format(name=name, enum=value))

    property_container = {}

    for name, value in enum.as_dict().items():
        if value not in property_container:
            property_container[value] = name

    properties = list(property_container.values())
    final.append(_properties.format(properties))

    return ('\n'*2).join(final)

_object_code = _create(ObjectDataEnum)
_color_code = _create(ColorChannelProperties)
