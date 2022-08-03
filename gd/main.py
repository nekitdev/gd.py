from platform import uname as system_version
from sys import exit
from typing import Iterator

import click
from aiohttp.web import Application

from gd.server.constants import DEFAULT_HOST, DEFAULT_PORT
from gd.server.core import run_app, setup_gd_app
from gd.string_utils import concat_new_line
from gd.version import python_version_info, version_info

__all__ = ("gd",)

PYTHON = "python"
LIBRARY = "gd.py"
SYSTEM = "system"

SYSTEM_VERSION = "{system.system} {system.release} {system.version}"
system_version_info = SYSTEM_VERSION.format(system=system_version())

VERSION = "- {} {}"

version_format = VERSION.format

VERSION_MAPPING = {
    PYTHON: str(python_version_info),
    LIBRARY: str(version_info),
    SYSTEM: system_version_info,
}


@click.option("--version", "-v", is_flag=True)
@click.group(invoke_without_command=True, no_args_is_help=True)
def gd(version: bool) -> None:
    if version:
        click.echo(concat_new_line(iter_versions()))
        exit()


def iter_versions() -> Iterator[str]:
    for name, version in VERSION_MAPPING.items():
        yield version_format(name, version)


SERVER = "server"


@click.option("--host", "-h", type=str, default=DEFAULT_HOST)
@click.option("--port", "-p", type=int, default=DEFAULT_PORT)
@gd.command(name=SERVER)
def server(host: str, port: int) -> None:
    app = Application()

    run_app(setup_gd_app(app), host=host, port=port)
