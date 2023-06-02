import click
import uvicorn

from gd.server.constants import DEFAULT_HOST, DEFAULT_PORT
from gd.server.core import app
from gd.version import version_info

__all__ = ("gd", "server")


@click.help_option("--help", "-h")
@click.version_option(str(version_info), "--version", "-V")
@click.group()
def gd() -> None:
    pass


@click.help_option("--help", "-h")
@click.option("--host", "-h", type=str, default=DEFAULT_HOST)
@click.option("--port", "-p", type=int, default=DEFAULT_PORT)
@gd.command()
def server(host: str, port: int) -> None:
    uvicorn.run(app, host=host, port=port)
