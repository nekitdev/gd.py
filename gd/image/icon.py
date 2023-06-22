from typing import Iterator, Optional

from attrs import define, field

from gd.assets import IMAGE_SUFFIX
from gd.color import Color
from gd.constants import DEFAULT_GLOW, DEFAULT_ICON_ID
from gd.enums import IconType
from gd.image.animation import Animation
from gd.image.layer import Layer
from gd.string_utils import concat_under, zero_pad

__all__ = ("Icon", "generate_name")

CUBE = "player"
SHIP = "ship"
BALL = "player_ball"
UFO = "bird"
WAVE = "dart"
ROBOT = "robot"
SPIDER = "spider"

ICON_TYPE_TO_NAME = {
    IconType.CUBE: CUBE,
    IconType.SHIP: SHIP,
    IconType.BALL: BALL,
    IconType.UFO: UFO,
    IconType.WAVE: WAVE,
    IconType.ROBOT: ROBOT,
    IconType.SPIDER: SPIDER,
}


EXTRA = "extra"
GLOW = "glow"

DEFAULT_EXTRA_COLOR = Color.white()
GLOW_COLOR_FALLBACK = Color.white()

DEFAULT_FRAME = 1

FULL_VALUE = 0xFF

ROBOT_VALUE_COUNT = 3
ROBOT_VALUE = 0xB2

SPIDER_VALUE_COUNT = 2
SPIDER_VALUE = 0x7F


@define()
class IconLayer:
    name: str
    color: Color


@define()
class ComplexIconLayer(IconLayer):
    layer: Layer
    value: int = FULL_VALUE

    @property
    def white(self) -> Color:
        value = self.value

        return Color.from_rgb(value, value, value)


@define()
class Icon:
    type: IconType = field(default=IconType.DEFAULT)
    id: int = field(default=DEFAULT_ICON_ID)
    color_1: Color = field(factory=Color.default_color_1)
    color_2: Color = field(factory=Color.default_color_2)
    glow: bool = field(default=DEFAULT_GLOW)
    idle: Optional[Animation] = field(default=None, repr=False)
    glow_color_unchecked: Optional[Color] = field(default=None, init=False, repr=False)
    extra_color_unchecked: Optional[Color] = field(default=None, init=False, repr=False)

    @property
    def name(self) -> str:
        return ICON_TYPE_TO_NAME[self.type]

    def has_glow(self) -> bool:
        return self.glow or self.color_1.is_black()

    def is_complex(self) -> bool:
        return self.type.is_robot() or self.type.is_spider()

    def is_simple(self) -> bool:
        return not self.is_complex()

    @property
    def glow_color(self) -> Color:
        glow_color = self.glow_color_unchecked

        if glow_color is None:
            color_2 = self.color_2

            if not color_2.is_black():
                return color_2

            color_1 = self.color_1

            if not color_1.is_black():
                return color_1

            return GLOW_COLOR_FALLBACK

        return glow_color

    @glow_color.setter
    def glow_color(self, color: Color) -> None:
        self.glow_color_unchecked = color

    @glow_color.deleter
    def glow_color(self) -> None:
        self.glow_color_unchecked = None

    @property
    def extra_color(self) -> Color:
        extra_color = self.extra_color_unchecked

        return DEFAULT_EXTRA_COLOR if extra_color is None else extra_color

    @extra_color.setter
    def extra_color(self, color: Color) -> None:
        self.extra_color_unchecked = color

    @extra_color.deleter
    def extra_color(self) -> None:
        self.extra_color_unchecked = None

    def generate_name(
        self,
        part: Optional[int] = None,
        sub_part: Optional[int] = None,
        extra: bool = False,
        glow: bool = False,
    ) -> str:
        return generate_name(
            name=self.name,
            id=self.id,
            part=part,
            sub_part=sub_part,
            extra=extra,
            glow=glow,
            frame=DEFAULT_FRAME,
            suffix=IMAGE_SUFFIX,
        )

    def get_value(self, index: int) -> int:
        if self.type.is_robot() and index < ROBOT_VALUE_COUNT:
            return ROBOT_VALUE

        if self.type.is_spider() and index < SPIDER_VALUE_COUNT:
            return SPIDER_VALUE

        return FULL_VALUE

    def iter_simple_layers(self) -> Iterator[IconLayer]:
        if self.is_complex():
            raise ValueError  # TODO: message?

        if self.has_glow():
            yield IconLayer(self.generate_name(glow=True), self.glow_color)

        if self.type.is_ufo():
            yield IconLayer(self.generate_name(sub_part=3), self.extra_color)

        yield IconLayer(self.generate_name(sub_part=2), self.color_2)
        yield IconLayer(self.generate_name(), self.color_1)

        yield IconLayer(self.generate_name(extra=True), self.extra_color)

    def iter_complex_layers(self) -> Iterator[ComplexIconLayer]:
        if self.is_simple():
            raise ValueError  # TODO: message?

        idle = self.idle

        if idle is None:
            raise ValueError  # TODO: message?

        frame = idle.single

        if frame is None:
            raise ValueError  # TODO: message?

        layers = frame.layers

        if self.has_glow():
            for layer in layers:
                yield ComplexIconLayer(
                    self.generate_name(part=layer.part, glow=True), self.glow_color, layer
                )

        for index, layer in enumerate(layers):
            yield ComplexIconLayer(
                self.generate_name(part=layer.part, sub_part=2),
                self.color_2,
                layer,
                self.get_value(index),
            )
            yield ComplexIconLayer(
                self.generate_name(part=layer.part), self.color_1, layer, self.get_value(index)
            )
            yield ComplexIconLayer(
                self.generate_name(part=layer.part, extra=True),
                self.extra_color,
                layer,
                self.get_value(index),
            )


def generate_name(
    name: str,
    id: Optional[int] = None,
    part: Optional[int] = None,
    sub_part: Optional[int] = None,
    extra: bool = False,
    glow: bool = False,
    frame: Optional[int] = None,
    suffix: Optional[str] = None,
) -> str:
    string = concat_under(
        generate_name_iterator(
            name=name, id=id, part=part, sub_part=sub_part, extra=extra, glow=glow, frame=frame
        )
    )

    return string if suffix is None else string + suffix


ID_ALIGN = 2
PART_ALIGN = 2
FRAME_ALIGN = 3


def generate_name_iterator(
    name: str,
    id: Optional[int] = None,
    part: Optional[int] = None,
    sub_part: Optional[int] = None,
    extra: bool = False,
    glow: bool = False,
    frame: Optional[int] = None,
) -> Iterator[str]:
    yield name

    if id is not None:
        yield zero_pad(ID_ALIGN, id)

    if part is not None:
        yield zero_pad(PART_ALIGN, part)

    if sub_part is not None:
        yield str(sub_part)

    if extra:
        yield EXTRA

    if glow:
        yield GLOW

    if frame is not None:
        yield zero_pad(FRAME_ALIGN, frame)
