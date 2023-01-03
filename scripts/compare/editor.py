import click
from entrypoint import entrypoint

from gd.client import Client
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.encoding import compress

LEVEL_ID = 37361518
ROUNDING = 2

FETCHING = "fetching level with ID {}..."
OPENING = "opening the editor..."
DUMPING = "dumping the editor..."
CONVERTING = "converting the editor..."

UNCOMPRESSED = "uncompressed: {} / {} ({}x compression)"
COMPRESSED = "compressed: {} / {} ({}x compression)"

client = Client()


@entrypoint(__name__)
@click.option("--level-id", "-l", default=LEVEL_ID, type=int)
@click.option("--rounding", "-r", default=ROUNDING, type=int)
@click.command()
def main(level_id: int, rounding: int) -> None:
    click.echo(FETCHING.format(level_id))

    level = client.run(client.get_level(level_id))

    click.echo(OPENING)

    editor = level.open_editor()

    click.echo(DUMPING)

    robtop_data = editor.to_robtop().encode(DEFAULT_ENCODING, DEFAULT_ERRORS)

    click.echo(CONVERTING)

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
