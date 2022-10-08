from typing import Iterable

from entrypoint import entrypoint
import click

from gd.api import ColorChannel, ColorChannels, Header
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.encoding import compress


def color_id_range(count: int) -> Iterable[int]:
    return range(1, count + 1)


COUNT = 1000
ROUNDING = 2

UNCOMPRESSED = "uncompressed: {} / {} ({}x compression)"
COMPRESSED = "compressed: {} / {} ({}x compression)"


@entrypoint(__name__)
@click.option("--count", "-c", default=COUNT)
@click.command()
def main(count: int) -> None:
    rounding = ROUNDING

    header = Header(
        color_channels=ColorChannels.from_color_channel_iterable(
            ColorChannel(color_id) for color_id in color_id_range(COUNT)
        )
    )

    robtop_data = header.to_robtop().encode(DEFAULT_ENCODING, DEFAULT_ERRORS)
    data = header.to_bytes()

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
