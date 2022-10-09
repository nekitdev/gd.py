import click
from entrypoint import entrypoint

from gd.api.color_channels import ColorChannel, ColorChannels
from gd.api.editor import Editor
from gd.api.header import Header
from gd.api.objects import Object
from gd.api.objects_constants import GRID_UNITS
from gd.color import Color
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.encoding import compress

COUNT = 1000
ROUNDING = 2

OBJECT_ID = 1

COLOR_ID = 1
COLOR = Color(0xFF0000)

UNCOMPRESSED = "uncompressed: {} / {} ({}x compression)"
COMPRESSED = "compressed: {} / {} ({}x compression)"


@entrypoint(__name__)
@click.option("--count", "-c", default=COUNT)
@click.command()
def main(count: int) -> None:
    grid_units = GRID_UNITS
    object_id = OBJECT_ID
    color_id = COLOR_ID
    rounding = ROUNDING

    header = Header(
        color_channels=ColorChannels.from_color_channels(ColorChannel(color_id, COLOR))
    )

    objects = [
        Object(
            object_id, x=index * grid_units, y=index * grid_units, base_color_id=color_id
        ) for index in range(count)
    ]

    editor = Editor(header, objects)

    robtop_data = editor.to_robtop().encode(DEFAULT_ENCODING, DEFAULT_ERRORS)
    data = editor.to_bytes()

    robtop_data_length = len(robtop_data)
    data_length = len(data)

    compression = round(robtop_data_length / data_length, rounding)

    click.echo(UNCOMPRESSED.format(data_length, robtop_data_length, compression))

    compressed_robtop_data = compress(robtop_data)
    compressed_data = compress(data)

    compressed_robtop_data_length = len(compressed_robtop_data)
    compressed_data_length = len(compressed_data)

    compressed_compression = round(compressed_robtop_data_length / compressed_data_length, rounding)

    click.echo(
        COMPRESSED.format(
            compressed_data_length, compressed_robtop_data_length, compressed_compression
        )
    )
