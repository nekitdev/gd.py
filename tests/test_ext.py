import pytest

try:
    import _gd
    not_test = False
except ImportError:
    not_test = True


@pytest.mark.skipif(not_test, reason='Extension module is not built.')
def test_extension():
    _gd.get_version()
