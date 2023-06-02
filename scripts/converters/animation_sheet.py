from pathlib import Path
from typing import Optional

import click
from entrypoint import entrypoint

from gd.image.converters import convert_animation_sheet_path


@entrypoint(__name__)
@click.option("--output", "-o", default=None, type=Path)
@click.option("--indent", "-i", default=None, type=int)
@click.argument("input", type=Path)
@click.command()
def convert_animation_sheet(input: Path, output: Optional[Path], indent: Optional[int]) -> None:
    convert_animation_sheet_path(input, output, indent)
