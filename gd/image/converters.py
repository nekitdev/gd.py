import json
import plistlib as plist  # NOTE: assuming valid plist files
import re
from collections import defaultdict as default_dict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypeVar

from iters.iters import iter
from typing_aliases import DynamicTuple, IntoPath, Parse, StringDict, Unary

from gd.assets import DATA_SUFFIX
from gd.constants import READ_BINARY, WRITE
from gd.errors import InternalError
from gd.image.animation import AnimationSheetData
from gd.image.layer import LayerData
from gd.image.sheet import SheetData
from gd.image.sprite import SpriteData
from gd.models_utils import int_bool
from gd.named_dicts import AnyCamelDict, CamelDict
from gd.string_constants import COMMA
from gd.string_utils import remove_braces, tick

__all__ = (
    "convert_animation_sheet_data",
    "convert_animation_sheet_path",
    "convert_sheet_data",
    "convert_sheet_path",
)

T = TypeVar("T")

MAGIC_SCALAR = 4


def parse_tuples(string: str, parse: Parse[T], separator: str = COMMA) -> DynamicTuple[T]:
    return iter(string.translate(remove_braces).split(separator)).map(parse).tuple()


def convert_sprite_format_0(sprite_dict: AnyCamelDict) -> SpriteData:
    x = float(sprite_dict.x)
    y = float(sprite_dict.y)
    width = float(sprite_dict.width)
    height = float(sprite_dict.height)
    offset_x = float(sprite_dict.offset_x)
    offset_y = float(sprite_dict.offset_y)

    return SpriteData(size=(width, height), offset=(offset_x, offset_y), location=(x, y))


def convert_sprite_format_1(sprite_dict: AnyCamelDict) -> SpriteData:
    (x, y, width, height) = parse_tuples(sprite_dict.frame, float)
    (offset_x, offset_y) = parse_tuples(sprite_dict.offset, float)

    return SpriteData(size=(width, height), offset=(offset_x, offset_y), location=(x, y))


def convert_sprite_format_2(sprite_dict: AnyCamelDict) -> SpriteData:
    (x, y, width, height) = parse_tuples(sprite_dict.frame, float)
    (offset_x, offset_y) = parse_tuples(sprite_dict.offset, float)

    rotated = bool(sprite_dict.rotated)

    return SpriteData(
        size=(width, height), offset=(offset_x, offset_y), location=(x, y), rotated=rotated
    )


def convert_sprite_format_3(sprite_dict: AnyCamelDict) -> SpriteData:
    (offset_x, offset_y) = parse_tuples(sprite_dict.sprite_offset, float)
    (x, y, width, height) = parse_tuples(sprite_dict.texture_rect, float)
    rotated = bool(sprite_dict.texture_rotated)

    return SpriteData(
        size=(width, height), offset=(offset_x, offset_y), location=(x, y), rotated=rotated
    )


ConvertSprite = Unary[AnyCamelDict, SpriteData]

FORMAT_0 = 0
FORMAT_1 = 1
FORMAT_2 = 2
FORMAT_3 = 3

convert_sprite_mapping: Dict[int, ConvertSprite] = {
    FORMAT_0: convert_sprite_format_0,
    FORMAT_1: convert_sprite_format_1,
    FORMAT_2: convert_sprite_format_2,
    FORMAT_3: convert_sprite_format_3,
}

CAN_NOT_CONVERT = "can not convert format {}"


def convert_sprite_format(format: int) -> ConvertSprite:
    convert_sprite = convert_sprite_mapping.get(format)

    if convert_sprite is None:
        raise ValueError(CAN_NOT_CONVERT.format(tick(format)))

    return convert_sprite


def convert_sheet_data(document: AnyCamelDict) -> SheetData:
    convert_sprite = convert_sprite_format(document.metadata.format)

    return {name: convert_sprite(sprite_dict) for name, sprite_dict in document.frames.items()}


def convert_sheet_path(
    input: IntoPath, output: Optional[IntoPath] = None, indent: Optional[int] = None
) -> None:
    input_path, output_path = input_output_path(input, output, DATA_SUFFIX)

    with input_path.open(READ_BINARY) as input_file:
        document = plist.load(input_file, dict_type=CamelDict)

    result = convert_sheet_data(document)

    with output_path.open(WRITE) as output_file:
        json.dump(result, output_file, indent=indent)


def convert_layer(layer_dict: AnyCamelDict) -> LayerData:
    part = get_layer_part(layer_dict.texture)
    position_x, position_y = parse_tuples(layer_dict.position, float)
    scale_width, scale_height = parse_tuples(layer_dict.scale, float)
    rotation = float(layer_dict.rotation)
    h_flipped, v_flipped = parse_tuples(layer_dict.flipped, int_bool)

    return LayerData(
        part=part,
        position=(position_x * MAGIC_SCALAR, position_y * MAGIC_SCALAR),  # NOTE: magic!
        scale=(scale_width, scale_height),
        rotation=rotation,
        h_flipped=h_flipped,
        v_flipped=v_flipped,
    )


def get_z(layer_dict: CamelDict[Any]) -> int:
    return int(layer_dict.z_value)


def convert_animation_sheet_data(document: AnyCamelDict) -> AnimationSheetData:
    data: StringDict[List[List[LayerData]]] = default_dict(list)

    for frame_name, frame_dict in document.animation_container.items():
        name, index = get_animation_name_index(frame_name)

        layer_dicts = sorted(frame_dict.values(), key=get_z)

        frame_data = iter(layer_dicts).map(convert_layer).list()

        data[name].insert(index, frame_data)

    return data


def convert_animation_sheet_path(
    input: IntoPath, output: Optional[IntoPath] = None, indent: Optional[int] = None
) -> None:
    input_path, output_path = input_output_path(input, output, DATA_SUFFIX)

    with input_path.open(READ_BINARY) as input_file:
        document = plist.load(input_file, dict_type=CamelDict)

    result = convert_animation_sheet_data(document)

    with output_path.open(WRITE) as output_file:
        json.dump(result, output_file, indent=indent)


def input_output_path(
    input: IntoPath, output: Optional[IntoPath], suffix: str
) -> Tuple[Path, Path]:
    input_path = Path(input)

    default_output_path = input_path.with_suffix(suffix)

    if output is None:
        output_path = default_output_path

    else:
        output_path = Path(output)

        if output_path.is_dir():
            output_path /= default_output_path.name

        output_path.parent.mkdir(parents=True, exist_ok=True)

    return (input_path, output_path)


FRAME_NAME = re.compile(
    r"^(?P<type>[A-Za-z0-9]+)_(?P<name>[A-Za-z0-9_]+)_(?P<frame>[0-9]+)\.(?P<suffix>.+)$"
)

LAYER_NAME = re.compile(
    r"^(?P<type>[A-Za-z0-9_]+)_(?P<id>[0-9]+)_(?P<part>[0-9]+)_(?P<frame>[0-9]+)\.(?P<suffix>.+)$"
)

FRAME = "frame"
NAME = "name"
PART = "part"


def get_animation_name_index(frame_name: str) -> Tuple[str, int]:
    match = FRAME_NAME.match(frame_name)

    if match is None:
        raise ValueError  # TODO: message?

    name = match.group(NAME)

    if name is None:
        raise InternalError  # TODO: message?

    frame_option = match.group(FRAME)

    if frame_option is None:
        raise InternalError  # TODO: message?

    frame = int(frame_option) - 1

    return (name, frame)


def get_layer_part(layer_name: str) -> int:
    match = LAYER_NAME.match(layer_name)

    if match is None:
        raise ValueError  # TODO: message?

    part_option = match.group(PART)

    if part_option is None:
        raise InternalError  # TODO: message?

    part = int(part_option)

    return part
