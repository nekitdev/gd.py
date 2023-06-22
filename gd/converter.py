from typing import TypeVar

from attrs import field, frozen
from cattrs import Converter
from cattrs.gen import AttributeOverride, make_dict_unstructure_fn, override
from typing_aliases import AnyType, StringDict

__all__ = (
    "CONVERTER",
    "register_unstructure_hook",
    "register_unstructure_hook_omit_client",
)

CONVERTER = Converter(forbid_extra_keys=True)

AttributeOverrides = StringDict[AttributeOverride]

T = TypeVar("T", bound=AnyType)


@frozen()
class RegisterUnstructureHook:
    overrides: AttributeOverrides = field(factory=dict, repr=False)

    def __call__(self, type: T) -> T:
        CONVERTER.register_unstructure_hook(
            type, make_dict_unstructure_fn(type, CONVERTER, **self.overrides)  # type: ignore
        )

        return type


def register_unstructure_hook(**overrides: AttributeOverride) -> RegisterUnstructureHook:
    return RegisterUnstructureHook(overrides)


register_unstructure_hook_omit_client = register_unstructure_hook(
    client_unchecked=override(omit=True)
)
