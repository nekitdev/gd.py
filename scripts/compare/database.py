from entrypoint import entrypoint

from gd.api.save_manager import save
from gd.encoding import compress

ROUNDING = 2

UNCOMPRESSED = "uncompressed: {} / {} ({}x compression)"
COMPRESSED = "compressed: {} / {} ({}x compression)"

LOADING = "Loading the database..."
DUMPING = "Dumping the database..."
CONVERTING = "Converting the database..."
COMPRESSING = "Compressing the database..."


@entrypoint(__name__)
def main() -> None:
    rounding = ROUNDING

    print(LOADING)

    database = save.load()

    print(DUMPING)

    robtop_data = database.dump_main() + database.dump_levels()

    print(CONVERTING)

    data = database.to_bytes()

    robtop_data_length = len(robtop_data)
    data_length = len(data)

    compression = round(robtop_data_length / data_length, rounding)

    print(UNCOMPRESSED.format(data_length, robtop_data_length, compression))

    print(COMPRESSING)

    compressed_robtop_data = compress(robtop_data)
    compressed_data = compress(data)

    compressed_robtop_data_length = len(compressed_robtop_data)
    compressed_data_length = len(compressed_data)

    compressed_compression = round(compressed_robtop_data_length / compressed_data_length, rounding)

    print(
        COMPRESSED.format(
            compressed_data_length, compressed_robtop_data_length, compressed_compression
        )
    )
