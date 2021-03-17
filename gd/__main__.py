"""Somewhat useful 'python -m gd' implementation"""

import asyncio
import platform

import aiohttp
import click

import gd

from gd.typing import Iterator

HOST = "0.0.0.0"
PORT = 8080

NEWLINE = "\n"


@click.option("--version", "-v", is_flag=True, help="Show different versions of software.")
@click.group(invoke_without_command=True, no_args_is_help=True)
def group(version: bool) -> None:
    if version:
        click.echo(NEWLINE.join(collect_versions()))


@click.option("--host", type=str, default=HOST, help="Host to serve the application on.")
@click.option("--port", type=int, default=PORT, help="Port to serve the application on.")
@group.command(short_help="Run gd.server web application.")
def server(host: str, port: int) -> None:
    gd.server.run_gd_sync(host=host, port=port)


@group.command(
    short_help="Run IPython console, with aiohttp, asyncio and gd added to namespace."
)
def console() -> None:
    from IPython import start_ipython  # type: ignore

    start_ipython(argv=[], user_ns=dict(aiohttp=aiohttp, asyncio=asyncio, gd=gd))


def version_from_info(version_info: gd.VersionInfo) -> str:
    return "{0.major}.{0.minor}.{0.micro}-{0.release_level}".format(version_info)


def version_from_system(system: platform.uname_result) -> str:
    return "{0.system} {0.release} {0.version}".format(system)


def collect_versions() -> Iterator[str]:
    yield f"- python {version_from_info(gd.python_version_info)}"
    yield f"- gd.py {version_from_info(gd.version_info)}"
    yield f"- aiohttp {aiohttp.__version__}"
    yield f"- click {click.__version__}"
    yield f"- system {version_from_system(platform.uname())}"


# run main
if __name__ == "__main__":
    group()
