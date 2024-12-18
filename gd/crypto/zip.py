from zlib import MAX_WBITS, Z_BEST_COMPRESSION
from zlib import compressobj as create_compressor
from zlib import decompressobj as create_decompressor

__all__ = ("compress", "decompress")

Z_GZIP_HEADER = 0x10


def compress(data: bytes) -> bytes:
    """Compresses given data.

    Arguments:
        data: The data to compress.

    Returns:
        The compressed data.
    """
    compressor = create_compressor(level=Z_BEST_COMPRESSION, wbits=MAX_WBITS | Z_GZIP_HEADER)

    return compressor.compress(data) + compressor.flush()


def decompress(data: bytes) -> bytes:
    """Decompresses given data.

    This function is the inverse of [`compress`][gd.crypto.zip.compress], meaning that

    ```python
    decompress(compress(data)) == data
    ```

    holds for any `data`.

    Arguments:
        data: The data to decompress.

    Returns:
        The decompressed data.
    """
    decompressor = create_decompressor(wbits=MAX_WBITS | Z_GZIP_HEADER)

    return decompressor.decompress(data) + decompressor.flush()
