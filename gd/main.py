import click

from gd.version import version_info

__all__ = ("gd",)


@click.help_option("--help", "-h")
@click.version_option(str(version_info), "--version", "-V")
@click.group()
def gd() -> None:
    pass
