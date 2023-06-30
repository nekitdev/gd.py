from __future__ import annotations

from os import getenv as get_environment
from pathlib import Path
from typing import Generic, Optional, Tuple, Type, TypeVar

from attrs import define
from typing_aliases import IntoPath

# from gd.asyncio import run_blocking
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.encoding import decode_save, decode_system_save, encode_save, encode_system_save
from gd.enums import Platform
from gd.platform import SYSTEM_PLATFORM

__all__ = (
    "MAIN_NAME",
    "LEVELS_NAME",
    "PATH",
    "SaveManager",
    "create_database",
    "save",
)

MAIN_NAME = "CCGameManager.dat"
LEVELS_NAME = "CCLocalLevels.dat"


HOME = Path.home()


LOCAL_APP_DATA_NAME = "LOCALAPPDATA"
LOCAL_APP_DATA_STRING = get_environment(LOCAL_APP_DATA_NAME)

APP_DATA = "AppData"
LOCAL = "Local"

if LOCAL_APP_DATA_STRING is None:
    LOCAL_APP_DATA = HOME / APP_DATA / LOCAL

else:
    LOCAL_APP_DATA = Path(LOCAL_APP_DATA_STRING)


GEOMETRY_DASH = "GeometryDash"
GEOMETRY_DASH_ID = 322170

LIBRARY = "Library"
APPLICATION_SUPPORT = "Application Support"

DOT_STEAM = ".steam"
STEAM = "steam"
STEAM_APPS = "steamapps"
COMPATIBILITY_DATA = "compatdata"
PFX = "pfx"

DRIVE_C = "drive_c"
USERS = "users"
STEAM_USER = "steamuser"
LOCAL_SETTINGS = "Local Settings"
APPLICATION_DATA = "Application Data"


WINDOWS_PATH = LOCAL_APP_DATA / GEOMETRY_DASH
DARWIN_PATH = HOME / LIBRARY / APPLICATION_SUPPORT / GEOMETRY_DASH
LINUX_PATH = (
    HOME
    / DOT_STEAM
    / STEAM
    / STEAM_APPS
    / COMPATIBILITY_DATA
    / str(GEOMETRY_DASH_ID)
    / PFX
    / DRIVE_C
    / USERS
    / STEAM_USER
    / LOCAL_SETTINGS
    / APPLICATION_DATA
    / GEOMETRY_DASH
)


PATHS = {
    Platform.WINDOWS: WINDOWS_PATH,
    Platform.DARWIN: DARWIN_PATH,
    Platform.LINUX: LINUX_PATH,
}


PATH = PATHS.get(SYSTEM_PLATFORM)

SAVE_NOT_SUPPORTED = "save management is not supported on this platform"

DEFAULT_FOLLOW_SYSTEM = False
DEFAULT_APPLY_XOR = False

DEFAULT_FOLLOW_SYSTEM_DATA = True
DEFAULT_APPLY_XOR_DATA = True

D = TypeVar("D", bound="Database")


@define()
class SaveManager(Generic[D]):
    database_type: Type[D]
    main_name: str = MAIN_NAME
    levels_name: str = LEVELS_NAME

    def create_database(self) -> D:
        return self.database_type()

    def load(self, main: Optional[IntoPath] = None, levels: Optional[IntoPath] = None) -> D:
        main_path = self.compute_path(main, self.main_name)
        levels_path = self.compute_path(levels, self.levels_name)

        main_data = main_path.read_bytes()
        levels_data = levels_path.read_bytes()

        return self.load_parts(main_data, levels_data, apply_xor=True, follow_system=True)

    def dump(
        self,
        database: Database,
        main: Optional[IntoPath] = None,
        levels: Optional[IntoPath] = None,
    ) -> None:
        main_path = self.compute_path(main, self.main_name)
        levels_path = self.compute_path(levels, self.levels_name)

        main_data, levels_data = self.dump_parts(database, apply_xor=True, follow_system=True)

        main_path.write_bytes(main_data)
        levels_path.write_bytes(levels_data)

    def load_parts(
        self,
        main_data: bytes,
        levels_data: bytes,
        apply_xor: bool = False,
        follow_system: bool = False,
    ) -> D:
        main = self.decode_data(main_data, apply_xor=apply_xor, follow_system=follow_system)
        levels = self.decode_data(levels_data, apply_xor=apply_xor, follow_system=follow_system)

        return self.database_type.load_parts(main, levels)

    def load_string_parts(
        self,
        main_string: str,
        levels_string: str,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
        apply_xor: bool = False,
        follow_system: bool = False,
    ) -> D:
        return self.load_parts(
            main_string.encode(encoding, errors),
            levels_string.encode(encoding, errors),
            apply_xor=apply_xor,
            follow_system=follow_system,
        )

    def dump_parts(
        self, database: Database, apply_xor: bool = False, follow_system: bool = False
    ) -> Tuple[bytes, bytes]:
        main_data = self.encode_data(
            database.dump_main(), apply_xor=apply_xor, follow_system=follow_system
        )
        levels_data = self.encode_data(
            database.dump_levels(), apply_xor=apply_xor, follow_system=follow_system
        )

        return (main_data, levels_data)

    def dump_string_parts(
        self,
        database: Database,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
        apply_xor: bool = False,
        follow_system: bool = False,
    ) -> Tuple[str, str]:
        main_data, levels_data = self.dump_parts(
            database, apply_xor=apply_xor, follow_system=follow_system
        )

        return (main_data.decode(encoding, errors), levels_data.decode(encoding, errors))

    def compute_path(self, base_path: Optional[IntoPath], additional_path: IntoPath) -> Path:
        if base_path is None:
            if PATH is None:
                raise OSError(SAVE_NOT_SUPPORTED)

            return PATH / additional_path

        path = Path(base_path)

        if path.is_dir():
            return path / additional_path

        return path

    def decode_data(
        self,
        data: bytes,
        apply_xor: bool = DEFAULT_APPLY_XOR_DATA,
        follow_system: bool = DEFAULT_FOLLOW_SYSTEM_DATA,
    ) -> bytes:
        decode = decode_system_save if follow_system else decode_save

        return decode(data, apply_xor=apply_xor)

    def encode_data(
        self,
        data: bytes,
        apply_xor: bool = DEFAULT_APPLY_XOR_DATA,
        follow_system: bool = DEFAULT_FOLLOW_SYSTEM_DATA,
    ) -> bytes:
        encode = encode_system_save if follow_system else encode_save

        return encode(data, apply_xor=apply_xor)


from gd.api.database.database import Database

save = SaveManager(Database)
create_database = save.create_database
