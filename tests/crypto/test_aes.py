from hypothesis import given, strategies

from gd.crypto.aes import append_padding, decrypt_aes, encrypt_aes, remove_padding


@given(data=strategies.binary())
def test_padding(data: bytes) -> None:
    assert remove_padding(append_padding(data)) == data


@given(data=strategies.binary())
def test_aes(data: bytes) -> None:
    assert decrypt_aes(encrypt_aes(data)) == data
