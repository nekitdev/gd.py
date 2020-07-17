from gd.typing import Iterable, List, Optional, Tuple, Union

from gd.abstractentity import AbstractEntity
from gd.colors import Color
from gd.icon_factory import ImageType, connect_images, factory, to_bytes

from gd.utils.async_utils import run_blocking_io
from gd.utils.enums import IconType
from gd.utils.text_tools import make_repr


class IconSet(AbstractEntity):
    """Class that represents an Icon Set."""

    ALL_TYPES = ("cube", "ship", "ball", "ufo", "wave", "robot", "spider")

    def __repr__(self) -> str:
        info = {
            "main_icon": self.main,
            "main_type": self.main_type,
            "color_1": self.color_1,
            "color_2": self.color_2,
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return f"IconSet{self.get_colors()}"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.options == other.options

    @property
    def id(self) -> int:
        """:class:`int`: ID of the icon set, based on colors and main icon."""
        return self.main + self.color_1.value + self.color_2.value + self.main_type.value

    @property
    def main(self) -> int:
        """:class:`int`: ID of the main icon of the iconset. (see :attr:`.IconSet.main_type`)"""
        return self.options.get("main_icon", 1)

    @property
    def color_1(self) -> Color:
        """:class:`.Color`: A first color of the iconset."""
        return self.options.get("color_1", Color(0x00FF00))

    @property
    def color_2(self) -> Color:
        """:class:`.Color`: A second color of the iconset."""
        return self.options.get("color_2", Color(0x00FFFF))

    @property
    def main_type(self) -> IconType:
        """:class:`.IconType`: A type of the main icon of the iconset."""
        return IconType.from_value(self.options.get("main_icon_type", 0))

    @property
    def cube(self) -> int:
        """:class:`int`: Cube ID of the iconset."""
        return self.options.get("icon_cube", 1)

    @property
    def ship(self) -> int:
        """:class:`int`: Ship ID of the iconset."""
        return self.options.get("icon_ship", 1)

    @property
    def ball(self) -> int:
        """:class:`int`: Ball ID of the iconset."""
        return self.options.get("icon_ball", 1)

    @property
    def ufo(self) -> int:
        """:class:`int`: UFO ID of the iconset."""
        return self.options.get("icon_ufo", 1)

    @property
    def wave(self) -> int:
        """:class:`int`: Wave ID of the iconset."""
        return self.options.get("icon_wave", 1)

    @property
    def robot(self) -> int:
        """:class:`int`: Robot ID of the iconset."""
        return self.options.get("icon_robot", 1)

    @property
    def spider(self) -> int:
        """:class:`int`: Spider ID of the iconset."""
        return self.options.get("icon_spider", 1)

    @property
    def explosion(self) -> int:
        """:class:`int`: Explosion ID of the iconset."""
        return self.options.get("icon_explosion", 1)

    def get_id_by_type(self, type: IconType) -> int:
        return getattr(self, type.name.lower(), 1)

    def has_glow_outline(self) -> bool:
        """:class:`bool`: Indicates whether an iconset has glow outline."""
        return self.options.get("has_glow_outline", False)

    def get_colors(self) -> Tuple[Color, Color]:
        """Tuple[:class:`.Color`, :class:`.Color`]: A shorthand for *color_1* and *color_2*."""
        return self.color_1, self.color_2

    async def generate(
        self, type: Optional[Union[int, str, IconType]] = None, as_image: bool = False,
    ) -> Union[bytes, ImageType]:
        """|coro|

        Generate an image of an icon.

        Parameters
        ----------
        type: Optional[Union[:class:`int`, :class:`str`, :class:`.IconType`]]
            Type of an icon to generate. If not given or ``"main"``, picks current main icon.

        as_image: :class:`bool`
            Whether to return an image or bytes of an image.

        Returns
        -------
        Union[:class:`bytes`, :class:`PIL.Image.Image`]
            Bytes or an image, based on ``as_image``.
        """
        if type is None or type == "main":
            type = self.main_type

        type = IconType.from_value(type)

        result = await run_blocking_io(
            factory.generate,
            icon_type=type,
            icon_id=self.get_id_by_type(type),
            color_1=self.color_1,
            color_2=self.color_2,
            glow_outline=self.has_glow_outline(),
        )

        if as_image:
            return result

        return await run_blocking_io(to_bytes, result)

    async def generate_many(
        self, *types: Iterable[Union[int, str, IconType]], as_image: bool = False,
    ) -> Union[List[bytes], List[ImageType]]:
        r"""|coro|

        Generate images of icons.

        Parameters
        ----------
        \*types: Iterable[Optional[Union[:class:`int`, :class:`str`, :class:`.IconType`]]]
            Types of icons to generate. If ``"main"`` is given, picks current main icon.

        as_image: :class:`bool`
            Whether to return images or bytes of images.

        Returns
        -------
        Union[List[:class:`bytes`], List[:class:`PIL.Image.Image`]]
            List of bytes or of images, based on ``as_image``.
        """
        return [await self.generate(type=type, as_image=as_image) for type in types]

    async def generate_image(
        self, *types: Iterable[Union[int, str, IconType]], as_image: bool = False,
    ) -> Union[bytes, ImageType]:
        r"""|coro|

        Generate images of icons and connect them into one image.

        Parameters
        ----------
        \*types: Iterable[Optional[Union[:class:`int`, :class:`str`, :class:`.IconType`]]]
            Types of icons to generate. If ``"main"`` is given, picks current main icon.

        as_image: :class:`bool`
            Whether to return an image or bytes of an image.

        Returns
        -------
        Union[:class:`bytes`, :class:`PIL.Image.Image`]
            Bytes or an image, based on ``as_image``.
        """
        images = await self.generate_many(*types, as_image=True)
        result = await run_blocking_io(connect_images, images)

        if as_image:
            return result

        return await run_blocking_io(to_bytes, result)

    async def generate_full(self, as_image: bool = False) -> Union[bytes, ImageType]:
        """|coro|

        Generate an image of the full icon set.

        Parameters
        ----------
        as_image: :class:`bool`
            Whether to return an image or bytes of an image.

        Returns
        -------
        Union[:class:`bytes`, :class:`PIL.Image.Image`]
            Bytes or an image, based on ``as_image``.
        """
        return await self.generate_image(*self.ALL_TYPES, as_image=as_image)
