from __future__ import annotations

from typing import Iterable, Optional, Tuple, Type, TypeVar

from attrs import define
from typing_aliases import IntoPath

from gd.asyncio import run_blocking
from gd.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH
from gd.errors import InternalError
from gd.image.geometry import Point, Rectangle, Size
from gd.image.sprite import Sprite

try:
    from PIL.Image import BICUBIC, LANCZOS, Image
    from PIL.Image import new as new_image
    from PIL.ImageOps import colorize, flip, grayscale, mirror

except ImportError:
    pass

from gd.assets import (
    GLOW_DATA_PATH,
    GLOW_IMAGE_PATH,
    ICON_DATA_PATH,
    ICON_IMAGE_PATH,
    ROBOT_ANIMATION_SHEET_PATH,
    SPIDER_ANIMATION_SHEET_PATH,
)
from gd.color import Color
from gd.enums import Orientation
from gd.image.animation import Animation, Animations, AnimationSheet
from gd.image.icon import Icon
from gd.image.sheet import Sheet
from gd.image.sprite import Sprites

__all__ = ("FACTORY", "Factory")

F = TypeVar("F", bound="Factory")

IDLE = "idle"

RGBA = "RGBA"

ZERO = 0

BLACK = Color.black()
EMPTY = BLACK.to_rgba(ZERO)


def connect_horizontal_images(images: Iterable[Image]) -> Image:
    array = list(images)

    width = sum(image.width for image in array)
    height = max((image.height for image in array), default=0)

    result = new_image(RGBA, (width, height), EMPTY)

    offset = 0

    for image in array:
        result.paste(image, (offset, 0))
        offset += image.width

    return result


def connect_vertical_images(images: Iterable[Image]) -> Image:
    array = list(images)

    width = max((image.width for image in array), default=0)
    height = sum(image.height for image in array)

    result = new_image(RGBA, (width, height), EMPTY)

    offset = 0

    for image in array:
        result.paste(image, (0, offset))
        offset += image.height

    return result


def connect_images(
    images: Iterable[Image], orientation: Orientation = Orientation.DEFAULT
) -> Image:
    if orientation.is_horizontal():
        return connect_horizontal_images(images)

    if orientation.is_vertical():
        return connect_vertical_images(images)

    raise InternalError  # TODO: message?


QUARTER = 90
HALF = 180
FULL = 360

UFO_OFFSET = 30.0


@define()
class Factory:
    icon_sheet: Sheet
    glow_sheet: Sheet
    robot_animation_sheet: AnimationSheet
    spider_animation_sheet: AnimationSheet

    @classmethod
    def default(cls: Type[F]) -> F:
        return cls.from_paths()

    @classmethod
    def from_paths(
        cls: Type[F],
        icon_image_path: IntoPath = ICON_IMAGE_PATH,
        icon_data_path: IntoPath = ICON_DATA_PATH,
        glow_image_path: IntoPath = GLOW_IMAGE_PATH,
        glow_data_path: IntoPath = GLOW_DATA_PATH,
        robot_animation_sheet_path: IntoPath = ROBOT_ANIMATION_SHEET_PATH,
        spider_animation_sheet_path: IntoPath = SPIDER_ANIMATION_SHEET_PATH,
    ) -> F:
        return cls(
            Sheet.from_paths(icon_image_path, icon_data_path),
            Sheet.from_paths(glow_image_path, glow_data_path),
            AnimationSheet.from_path(robot_animation_sheet_path),
            AnimationSheet.from_path(spider_animation_sheet_path),
        )

    @staticmethod
    def image_rectangle(image: Image) -> Rectangle:
        width, height = image.size

        return Rectangle(Point(), Size(width, height))

    @staticmethod
    def paint(image: Image, color: Color, black: Color = BLACK) -> Image:
        _red, _green, _blue, alpha = image.split()

        colored = colorize(
            grayscale(image), black=black.to_rgb(), white=color.to_rgb()  # type: ignore
        )

        colored.putalpha(alpha)

        return colored

    @property
    def robot_animations(self) -> Animations:
        return self.robot_animation_sheet.animations

    @property
    def spider_animations(self) -> Animations:
        return self.spider_animation_sheet.animations

    @property
    def icon_sprites(self) -> Sprites:
        return self.icon_sheet.sprites

    @property
    def glow_sprites(self) -> Sprites:
        return self.glow_sheet.sprites

    @property
    def icon_image(self) -> Image:
        return self.icon_sheet.image

    @property
    def glow_image(self) -> Image:
        return self.glow_sheet.image

    @property
    def robot_idle(self) -> Animation:
        return self.robot_animations[IDLE]

    @property
    def spider_idle(self) -> Animation:
        return self.spider_animations[IDLE]

    def ensure_loaded(self) -> None:
        self.icon_sheet.ensure_loaded()
        self.glow_sheet.ensure_loaded()
        self.robot_animation_sheet.ensure_loaded()
        self.spider_animation_sheet.ensure_loaded()

    def load(self) -> None:
        self.icon_sheet.load()
        self.glow_sheet.load()
        self.robot_animation_sheet.load()
        self.spider_animation_sheet.load()

    reload = load

    def unload(self) -> None:
        self.icon_sheet.unload()
        self.glow_sheet.unload()
        self.robot_animation_sheet.unload()
        self.spider_animation_sheet.unload()

    def find_sprite_and_image(self, name: str) -> Optional[Tuple[Sprite, Image]]:
        self.ensure_loaded()

        sprite = self.icon_sprites.get(name)

        if sprite is None:
            sprite = self.glow_sprites.get(name)

            if sprite is None:
                return None

            return (sprite, self.glow_image)

        return (sprite, self.icon_image)

    async def generate_async(
        self, icon: Icon, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT
    ) -> Image:
        self.ensure_loaded()

        return await run_blocking(self.generate, icon, width=width, height=height)

    def generate(
        self, icon: Icon, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT
    ) -> Image:
        self.ensure_loaded()

        # ensure `idle` is configured

        if icon.type.is_robot():
            icon.idle = self.robot_idle

        if icon.type.is_spider():
            icon.idle = self.spider_idle

        result = new_image(RGBA, (width, height), EMPTY)

        center = self.image_rectangle(result).center

        if icon.is_complex():
            for complex_icon_layer in icon.iter_complex_layers():
                search = self.find_sprite_and_image(complex_icon_layer.name)

                layer = complex_icon_layer.layer

                if search:
                    sprite, image = search

                    part = self.paint(
                        self.paint(image.crop(sprite.box), complex_icon_layer.white),
                        complex_icon_layer.color,
                    )

                    if sprite.is_rotated():
                        part = part.rotate(QUARTER, resample=BICUBIC, expand=True)

                    size = sprite.size.mul_components(layer.scale)

                    part = part.resize(size.round_tuple(), resample=LANCZOS)

                    if layer.is_h_flipped():
                        part = mirror(part)

                    if layer.is_v_flipped():
                        part = flip(part)

                    rotation = -layer.rotation  # NOTE: different rotation directions!

                    part = part.rotate(rotation, resample=BICUBIC, expand=True)

                    position = (
                        center
                        - self.image_rectangle(part).center
                        + sprite.offset.y_flipped()
                        + layer.position.y_flipped()
                    )

                    result.alpha_composite(part, position.round_tuple())

        else:
            for icon_layer in icon.iter_simple_layers():
                search = self.find_sprite_and_image(icon_layer.name)

                if search:
                    sprite, image = search

                    part = self.paint(image.crop(sprite.box), icon_layer.color)

                    if sprite.is_rotated():
                        part = part.rotate(QUARTER, resample=BICUBIC, expand=True)

                    position = (
                        center - self.image_rectangle(part).center + sprite.offset.y_flipped()
                    )

                    if icon.type.is_ufo():
                        position.y += UFO_OFFSET

                    result.alpha_composite(part, position.round_tuple())

        return result


FACTORY = Factory.default()
