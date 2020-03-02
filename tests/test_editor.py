import gd

from conftest import client


def make_editor():
    editor = gd.api.Editor()
    editor.add_objects(
        *(gd.api.Object(id=1, x=n*30, y=n*30) for n in range(100))
    )
    return editor


def test_open_editor():
    level = client.run(client.get_level(30029017))
    assert level.open_editor().objects


def test_get_length():
    editor = make_editor()
    assert editor.get_length()
