from pathlib import Path
import functools
import os
import sys

from gd.typing import Optional, Tuple, Union

from gd.utils.async_utils import run_blocking_io
from gd.utils.crypto.coders import Coder
from gd.utils.text_tools import make_repr

from gd.api.save import Database

__all__ = ("SaveUtil", "get_path", "save", "make_db", "set_path", "encode_save", "decode_save")

MAIN = "CCGameManager.dat"
LEVELS = "CCLocalLevels.dat"
MACOS = False

PathLike = Union[str, Path]

try:
    if sys.platform == "win32":
        path = Path(os.getenv("localappdata")) / "GeometryDash"

    elif sys.platform == "darwin":
        MACOS = True
        path = Path("~/Library/Application Support/GeometryDash").expanduser()

    else:
        path = Path()

except Exception:
    path = Path()


def set_path(new_path: Path) -> None:
    global path
    path = new_path


def get_path() -> Path:
    return path


if MACOS:
    decode_save, encode_save = Coder.decode_mac_save, Coder.encode_mac_save
else:
    decode_save, encode_save = Coder.decode_save, Coder.encode_save


class SaveUtil:
    def __repr__(self) -> str:
        return make_repr(self)

    async def load_async(self, *args, **kwargs) -> Database:
        """|coro|

        Asynchronously load a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            database = await gd.api.save.load_async()

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        main: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing main part of the save.
        levels: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing levels part of the save.
        main_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.
        levels_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.

        Returns
        -------
        :class:`.api.Database`
            Loaded Database. If any of the files not found, returns an empty ``gd.api.Database()``.
        """
        return await run_blocking_io(self._local_load, *args, **kwargs)

    def load(self, *args, **kwargs) -> Database:
        """Load a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            database = gd.api.save.load()

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        main: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing main part of the save.
        levels: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing levels part of the save.
        main_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.
        levels_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.

        Returns
        -------
        :class:`.api.Database`
            Loaded Database. If any of the files not found, returns an empty ``gd.api.Database()``.
        """
        return self._local_load(*args, **kwargs)

    async def dump_async(self, *args, **kwargs) -> None:
        """|coro|

        Asynchronously dump a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            await gd.api.save.dump_async(database)

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        db: :class:`.api.Database`
            Database object to dump.
        main: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing main part of the save.
        levels: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing levels part of the save.
        main_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.
        levels_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.
        """
        await run_blocking_io(self._local_dump, *args, **kwargs)

    def dump(self, *args, **kwargs) -> None:
        """Dump a save.

        This function is normally used for local GD management.
        Typical use-case might be, as follows:

        .. code-block:: python3

            gd.api.save.dump(database)

        .. warning::

            Please note that ``main_file`` and ``levels_file`` can **NOT** be ``None``.

        Parameters
        ----------

        db: :class:`.api.Database`
            Database object to dump.
        main: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing main part of the save.
        levels: Optional[Union[:class:`str`, :class:`pathlib.Path`]]
            Path to a file/directory containing levels part of the save.
        main_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing main part of the save.
            Applied when ``main`` is a directory.
        levels_file: Union[:class:`str`, :class:`pathlib.Path`]
            Path to a file containing levels part of the save.
            Applied when ``levels`` is a directory.
        """
        return self._local_dump(*args, **kwargs)

    async def to_string_async(self, *args, **kwargs) -> str:
        """|coro|

        Asynchronously dump a save into string(s).

        This might be used when you need to transfer your save a stream.

        Parameters
        ----------

        db: :class:`.api.Database`
            Database object to dump.
        connect: :class:`bool`
            Whether to join all strings with ``;`` into one string. Default is ``True``.
        xor: :class:`bool`
            Whether to apply *XOR* after zipping the save. (GD does that for local files)
            Defaults to ``False``.

        Returns
        -------
        Union[:class:`str`, Tuple[:class:`str`, :class:`str`]]
            A string or a tuple of strings containing the save.
        """
        return await run_blocking_io(functools.partial(self._dump, *args, **kwargs))

    def to_string(self, *args, **kwargs) -> str:
        """Dump a save into strings(s).

        This might be used when you need to transfer your save a stream.

        Parameters
        ----------

        db: :class:`.api.Database`
            Database object to dump.
        connect: :class:`bool`
            Whether to join all strings with ``;`` into one string. Default is ``True``.
        xor: :class:`bool`
            Whether to apply *XOR* after zipping the save. (GD does that for local files)
            Defaults to ``False``.

        Returns
        -------
        Union[:class:`str`, Tuple[:class:`str`, :class:`str`]]
            A string or a tuple of strings containing the save.
        """
        return self._dump(*args, **kwargs)

    async def from_string_async(self, *args, **kwargs) -> Database:
        """|coro|

        Asynchronoulsy load save from strings.

        Parameters
        ----------

        main: Union[:class:`bytes`, :class:`str`]
            A stream containing main part of the save.
        levels: Union[:class:`bytes`, :class:`str`]
            A stream containing levels part of the save.
        xor: :class:`bool`
            Whether to apply *XOR 11* to a string. (used in local GD saves)
            Defautls to ``False``.

        Returns
        -------
        :class:`.api.Database`
            Database object containing loaded data.
        """
        return await run_blocking_io(functools.partial(self._load, *args, **kwargs))

    def from_string(self, *args, **kwargs) -> Database:
        """Load save from strings.

        Parameters
        ----------

        main: Union[:class:`bytes`, :class:`str`]
            A stream containing main part of the save.
        levels: Union[:class:`bytes`, :class:`str`]
            A stream containing levels part of the save.
        xor: :class:`bool`
            Whether to apply *XOR 11* to a string. (used in local GD saves)
            Defautls to ``False``.

        Returns
        -------
        :class:`.api.Database`
            Database object containing loaded data.
        """
        return self._load(*args, **kwargs)

    def make_db(self, main: str = "", levels: str = "") -> Database:
        """Create a database from string parts.

        This method should be used if you already have XML strings, or it can be used
        as a more understandable way of doing ``gd.api.Database()`` creation:

        .. code-block:: python3

            db = gd.api.save.make_db()  # or supply arguments

        Parameters
        ----------

        main: :class:`str`
            A string containing main XML part of the save.
        levels: :class:`str`
            A string containing levels XML part of the save.

        Returns
        -------
        :class:`.api.Database`
            Database object containing loaded data.
        """
        return Database(main, levels)

    def _decode(self, stream: Union[bytes, str], xor: bool = True, follow_os: bool = True) -> str:
        if follow_os:
            global decode_save  # pull from global
        else:
            decode_save = Coder.decode_save

        try:
            return decode_save(stream, needs_xor=xor)
        except Exception:
            return ""

    def _load(
        self,
        main: Union[bytes, str] = "",
        levels: Union[bytes, str] = "",
        xor: bool = False,
        follow_os: bool = True,
    ) -> Database:
        main = self._decode(main, xor=xor, follow_os=follow_os)
        levels = self._decode(levels, xor=xor, follow_os=follow_os)
        return Database(main, levels)

    def _dump(
        self, db: Database, connect: bool = True, xor: bool = False, follow_os: bool = True
    ) -> Union[str, Tuple[str, str]]:
        if follow_os:
            global encode_save  # pull from global
        else:
            encode_save = Coder.encode_save

        parts = []

        for part in db.as_tuple():
            parts.append(encode_save(part.dump(), needs_xor=xor))

        main, levels, *_ = parts

        if connect:
            return main + ";" + levels
        else:
            return main, levels

    def _local_load(
        self,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> Database:
        main_path = _config_path(main, main_file)
        levels_path = _config_path(levels, levels_file)

        try:
            parts = []

            for path in (main_path, levels_path):

                with open(path, "rb") as file:
                    parts.append(file.read())

            return self._load(*parts, xor=True)

        except OSError:
            return self.make_db()

    def _local_dump(
        self,
        db: Database,
        main: Optional[PathLike] = None,
        levels: Optional[PathLike] = None,
        main_file: PathLike = MAIN,
        levels_file: PathLike = LEVELS,
    ) -> None:
        main_path = _config_path(main, main_file)
        levels_path = _config_path(levels, levels_file)

        files = (main_path, levels_path)

        for file, part in zip(files, db.as_tuple()):

            with open(file, "w") as data_file:
                data_file.write(encode_save(part.dump(), needs_xor=True))


def _config_path(some_path: PathLike, default: PathLike) -> Path:
    try:
        p = Path(some_path)

        if p.is_dir():
            return p / default

        return p

    except Exception:
        return path / default


save = SaveUtil()
make_db = save.make_db
