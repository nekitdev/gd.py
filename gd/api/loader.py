import os
from pathlib import Path

from gd.async_utils import run_blocking
from gd.crypto import (
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    decode_os_save,
    encode_os_save,
    decode_save,
    encode_save,
)
from gd.logging import get_logger
from gd.platform import LINUX, MACOS, WINDOWS
from gd.text_utils import make_repr
from gd.typing import AnyStr, Optional, Tuple, Union

from gd.api.database import Database

__all__ = ("MAIN", "LEVELS", "PATH", "SAVE_DELIM", "SaveUtils", "create_db", "save")

PathLike = Union[str, Path]

MAIN = "CCGameManager.dat"
LEVELS = "CCLocalLevels.dat"

PATH = Path()

LOCAL_APP_DATA = os.getenv("localappdata", "")

SAVE_DELIM = ";"

WINDOWS_DIR = LOCAL_APP_DATA + "/GeometryDash"
MACOS_DIR = "~/Library/Application Support/GeometryDash"
LINUX_DIR = (
    "~/.steam/steam/steamapps/compatdata/322170/pfx"
    "/drive_c/users/steamuser/Local Settings/Application Data/GeometryDash"
)

log = get_logger(__name__)

try:
    if WINDOWS:
        if not LOCAL_APP_DATA:
            raise FileNotFoundError("Can not find Local AppData folder.")

        PATH = Path(WINDOWS_DIR)

    elif MACOS:
        PATH = Path(MACOS_DIR).expanduser()

    elif LINUX:
        PATH = Path(LINUX_DIR).expanduser()

    else:
        raise OSError("Current platform is not supported.")

except Exception:  # noqa
    log.error("Can not find relevant GD PATH.", exc_info=True)


class SaveUtils:
    def __repr__(self) -> str:
        return make_repr(self)

    async def load_async(
        self,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> Database:
        """Asynchronously load a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            database = await gd.api.save.load_async()

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        main: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing main part of the save.

        levels: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing levels part of the save.

        main_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.

        levels_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.

        Returns
        -------
        :class:`~gd.api.Database`
            Loaded Database. If any of the files not found, returns an empty ``gd.api.Database()``.
        """
        return await run_blocking(
            self.local_load, main=main, levels=levels, main_file=main_file, levels_file=levels_file,
        )

    def load(
        self,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> Database:
        """Load a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            database = gd.api.save.load()

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        main: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing main part of the save.

        levels: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing levels part of the save.

        main_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.

        levels_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.

        Returns
        -------
        :class:`~gd.api.Database`
            Loaded Database. If any of the files not found, returns an empty ``gd.api.Database()``.
        """
        return self.local_load(
            main=main, levels=levels, main_file=main_file, levels_file=levels_file
        )

    async def dump_async(
        self,
        db: Database,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> None:
        """Asynchronously dump a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            await gd.api.save.dump_async(database)

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        db: :class:`~gd.api.Database`
            Database object to dump.

        main: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing main part of the save.

        levels: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing levels part of the save.

        main_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.

        levels_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.
        """
        await run_blocking(
            self.local_dump,
            db=db,
            main=main,
            levels=levels,
            main_file=main_file,
            levels_file=levels_file,
        )

    def dump(
        self,
        db: Database,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> None:
        """Dump a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            gd.api.save.dump(database)

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        db: :class:`~gd.api.Database`
            Database object to dump.

        main: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing main part of the save.

        levels: Optional[Union[:class:`str`, :class:`~pathlib.Path`]]
            Path to a file/directory containing levels part of the save.

        main_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.

        levels_file: Union[:class:`str`, :class:`~pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.
        """
        self.local_dump(
            db=db, main=main, levels=levels, main_file=main_file, levels_file=levels_file,
        )

    async def to_string_async(
        self, db: Database, apply_xor: bool = False, follow_os: bool = False, decode: bool = False,
    ) -> Union[Tuple[bytes, bytes], Tuple[str, str]]:
        """Asynchronously dump a save into strings.

        This might be used when you need to transfer your save as a stream.

        Parameters
        ----------

        db: :class:`~gd.api.Database`
            Database object to dump.

        apply_xor: :class:`bool`
            Whether to apply *XOR* function to given data (used by local saves mostly).

        follow_os: :class:`bool`
            Whether to use same encoding as in local saves on the given OS.

        decode: :class:`bool`
            Whether to convert :class:`bytes` to :class:`str` before returning.

        Returns
        -------
        Union[Tuple[:class:`bytes`, :class:`bytes`], Tuple[:class:`str`, :class:`str`]]
            A ``(main, levels)`` tuple, containing strings or bytes depending on ``decode``.
        """
        main, levels = await run_blocking(
            self.dump_parts, db=db, apply_xor=apply_xor, follow_os=follow_os
        )

        if decode:
            return (
                main.decode(DEFAULT_ENCODING, DEFAULT_ERRORS),
                levels.decode(DEFAULT_ENCODING, DEFAULT_ERRORS),
            )

        return (main, levels)

    def to_string(
        self, db: Database, apply_xor: bool = False, follow_os: bool = False, decode: bool = False,
    ) -> Union[Tuple[bytes, bytes], Tuple[str, str]]:
        """Dump a save into strings.

        This might be used when you need to transfer your save a stream.

        Parameters
        ----------

        db: :class:`~gd.api.Database`
            Database object to dump.

        apply_xor: :class:`bool`
            Whether to apply *XOR* function to given data (used by local saves mostly).

        follow_os: :class:`bool`
            Whether to use same encoding as in local saves on the given OS.

        decode: :class:`bool`
            Whether to convert :class:`bytes` to :class:`str` before returning.

        Returns
        -------
        Union[Tuple[:class:`bytes`, :class:`bytes`], Tuple[:class:`str`, :class:`str`]]
            A ``(main, levels)`` tuple, containing strings or bytes depending on ``decode``.
        """
        main, levels = self.dump_parts(db=db, apply_xor=apply_xor, follow_os=follow_os)

        if decode:
            return (
                main.decode(DEFAULT_ENCODING, DEFAULT_ERRORS),
                levels.decode(DEFAULT_ENCODING, DEFAULT_ERRORS),
            )

        return (main, levels)

    async def from_string_async(
        self,
        main: AnyStr = "",
        levels: AnyStr = "",
        apply_xor: bool = False,
        follow_os: bool = False,
    ) -> Database:
        """Asynchronoulsy load save from strings.

        Parameters
        ----------

        main: Union[:class:`bytes`, :class:`str`]
            A string containing encoded main part of the save.

        levels: Union[:class:`bytes`, :class:`str`]
            A string containing encoded levels part of the save.

        apply_xor: :class:`bool`
            Whether to apply *XOR* function to given data (used by local saves mostly).

        follow_os: :class:`bool`
            Whether to use same decoding as in local saves on the given OS.

        Returns
        -------
        :class:`~gd.api.Database`
            Database object containing loaded data.
        """
        return await run_blocking(
            self.load_parts, main=main, levels=levels, apply_xor=apply_xor, follow_os=follow_os,
        )

    def from_string(
        self,
        main: AnyStr = "",
        levels: AnyStr = "",
        apply_xor: bool = False,
        follow_os: bool = False,
    ) -> Database:
        """Load save from strings.

        Parameters
        ----------

        main: Union[:class:`bytes`, :class:`str`]
            A string containing encoded main part of the save.

        levels: Union[:class:`bytes`, :class:`str`]
            A string containing encoded levels part of the save.

        apply_xor: :class:`bool`
            Whether to apply *XOR* function to given data (used by local saves mostly).

        follow_os: :class:`bool`
            Whether to use same decoding as in local saves on the given OS.

        Returns
        -------
        :class:`~gd.api.Database`
            Database object containing loaded data.
        """
        return self.load_parts(main=main, levels=levels, apply_xor=apply_xor, follow_os=follow_os)

    def create_db(self, main: AnyStr = "", levels: AnyStr = "") -> Database:
        """Create a database from string parts.

        This method should be used if you already have XML strings, or it can be used
        as a more understandable way of doing ``gd.api.Database()`` creation:

        .. code-block:: python3

            db = gd.api.save.make_db()  # or supply arguments

        Parameters
        ----------

        main: Union[:class:`bytes`, :class:`str`]
            A string containing main XML part of the save.

        levels: Union[:class:`bytes`, :class:`str`]
            A string containing levels XML part of the save.

        Returns
        -------
        :class:`~gd.api.Database`
            Database object containing loaded data.
        """
        return Database(main, levels)

    def decode_stream(self, stream: bytes, apply_xor: bool = True, follow_os: bool = True) -> bytes:
        decoder = decode_os_save if follow_os else decode_save
        return decoder(stream, apply_xor=apply_xor)

    def encode_stream(self, stream: bytes, apply_xor: bool = True, follow_os: bool = True) -> bytes:
        encoder = encode_os_save if follow_os else encode_save
        return encoder(stream, apply_xor=apply_xor)

    def encode_if_str(self, bytes_or_str: AnyStr) -> bytes:
        if isinstance(bytes_or_str, str):
            return bytes_or_str.encode(DEFAULT_ENCODING, DEFAULT_ERRORS)

        return bytes_or_str

    def load_parts(
        self,
        main: AnyStr = "",
        levels: AnyStr = "",
        apply_xor: bool = False,
        follow_os: bool = False,
    ) -> Database:
        main_decoded = self.decode_stream(
            self.encode_if_str(main), apply_xor=apply_xor, follow_os=follow_os
        )
        levels_decoded = self.decode_stream(
            self.encode_if_str(levels), apply_xor=apply_xor, follow_os=follow_os
        )

        return Database(main_decoded, levels_decoded)

    def dump_parts(
        self, db: Database, apply_xor: bool = False, follow_os: bool = False
    ) -> Tuple[bytes, bytes]:
        main = self.encode_stream(
            self.encode_if_str(db.main.dump()), apply_xor=apply_xor, follow_os=follow_os
        )
        levels = self.encode_stream(
            self.encode_if_str(db.levels.dump()), apply_xor=apply_xor, follow_os=follow_os,
        )

        return (main, levels)

    @staticmethod
    def get_path(path_or_dir: Optional[PathLike], path: PathLike) -> PathLike:
        if path_or_dir is None:
            return PATH / path

        path_or_dir = Path(path_or_dir)

        if path_or_dir.is_dir():
            return path_or_dir / path

        return path_or_dir

    def local_load(
        self,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> Database:
        main_path = self.get_path(main, main_file)
        levels_path = self.get_path(levels, levels_file)

        try:
            with open(main_path, "rb") as file:
                main_stream = file.read()

            with open(levels_path, "rb") as file:
                levels_stream = file.read()

            return self.load_parts(main_stream, levels_stream, apply_xor=True, follow_os=True)

        except OSError:
            return self.create_db()

    def local_dump(
        self,
        db: Database,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> None:
        main_path = self.get_path(main, main_file)
        levels_path = self.get_path(levels, levels_file)

        main_stream, levels_stream = self.dump_parts(db, apply_xor=True, follow_os=True)

        with open(main_path, "wb") as file:
            file.write(main_stream)

        with open(levels_path, "wb") as file:
            file.write(levels_stream)


save = SaveUtils()
create_db = save.create_db
