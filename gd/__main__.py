"""Somewhat useful 'python -m gd' implementation"""

import platform
import sys
from typing import Any, Generator

import aiohttp
import click
import gd


@click.option("--version", "-v", is_flag=True, help="Show different versions of software.")
@click.group(invoke_without_command=True, no_args_is_help=True)
def gd_group(version: bool) -> None:
    if version:
        click.echo("\n".join(collect_versions()))


@gd_group.command(short_help="Run gd.server web application.")
def server() -> None:
    gd.server.start()


@gd_group.command(short_help="Run IPython console, with aiohttp and gd added to namespace.")
def console() -> None:
    from IPython import start_ipython

    start_ipython(argv=[], user_ns={"aiohttp": aiohttp, "gd": gd})


def version_from_info(version_info: Any) -> str:
    return "v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(version_info)


def collect_versions() -> Generator[str, None, None]:
    yield f"- python {version_from_info(sys.version_info)}"
    yield f"- gd.py {version_from_info(gd.version_info)}"
    yield f"- aiohttp v{aiohttp.__version__}"
    yield f"- click v{click.__version__}"
    yield "- system {0.system} {0.release} {0.version}".format(platform.uname())


# run main
if __name__ == "__main__":
    gd_group()
