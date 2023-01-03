import click
from entrypoint import entrypoint

from gd.api.save_manager import save
from gd.encoding import compress

ROUNDING = 2

UNCOMPRESSED = "uncompressed: {} / {} ({}x compression)"
COMPRESSED = "compressed: {} / {} ({}x compression)"

LOADING = "loading the database..."
DUMPING = "dumping the database..."
CONVERTING = "converting the database..."


@entrypoint(__name__)
@click.option("--rounding", "-r", default=ROUNDING, type=int)
@click.command()
def main(rounding: int) -> None:
    click.echo(LOADING)

    database = save.load()

    click.echo(DUMPING)

    robtop_data = database.dump_main() + database.dump_levels()

    click.echo(CONVERTING)

    data = database.to_bytes()

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
