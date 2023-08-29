# `gd.py`

[![License][License Badge]][License]
[![Version][Version Badge]][Package]
[![Downloads][Downloads Badge]][Package]
[![Discord][Discord Badge]][Discord]

[![Documentation][Documentation Badge]][Documentation]
[![Check][Check Badge]][Actions]
[![Test][Test Badge]][Actions]
[![Coverage][Coverage Badge]][Coverage]

> *An API wrapper for Geometry Dash written in Python.*

## Installing

**Python 3.7 or above is required.**

### pip

Installing the library with `pip` is quite simple:

```console
$ pip install gd.py
```

Alternatively, the library can be installed from source:

```console
$ git clone https://github.com/nekitdev/gd.py.git
$ cd gd.py
$ python -m pip install .
```

### poetry

You can add `gd.py` as a dependency with the following command:

```console
$ poetry add gd.py
```

Or by directly specifying it in the configuration like so:

```toml
[tool.poetry.dependencies]
"gd.py" = "^1.0.1"
```

Alternatively, you can add it directly from the source:

```toml
[tool.poetry.dependencies."gd.py"]
git = "https://github.com/nekitdev/gd.py.git"
```

## Examples

### Fetching

```python
# file.py

import asyncio

import gd

SONG_ID = 1081309
SONG = "{} by {} (ID: {}, size: {} MB)"


async def main() -> None:
    client = gd.Client()

    song = await client.get_song(SONG_ID)

    print(SONG.format(song.name, song.artist.name, song.id, song.size))


asyncio.run(main())
```

```console
$ python file.py
PANDA EYES - BROKEN by PandaEyesOfficial (ID: 1081309, size: 9.71 MB)
```

### Listening

```python
import gd

client = gd.Client()

DAILY = "new daily! {daily.name} by {daily.creator.name} (ID: {daily.id})"


@client.event
async def on_daily(daily: gd.Level) -> None:
    print(DAILY.format(daily=daily))


client.listen_for_daily()

client.create_controller().run()
```

## Documentation

You can find the documentation [here][Documentation].

## Support

If you need support with the library, you can send an [email][Email]
or refer to the official [Discord server][Discord].

## Changelog

You can find the changelog [here][Changelog].

## Security Policy

You can find the Security Policy of `gd.py` [here][Security].

## Contributing

If you are interested in contributing to `gd.py`, make sure to take a look at the
[Contributing Guide][Contributing Guide], as well as the [Code of Conduct][Code of Conduct].

## License

`gd.py` is licensed under the MIT License terms. See [License][License] for details.

[Email]: mailto:support@nekit.dev

[Discord]: https://nekit.dev/discord

[Actions]: https://github.com/nekitdev/gd.py/actions

[Changelog]: https://github.com/nekitdev/gd.py/blob/main/CHANGELOG.md
[Code of Conduct]: https://github.com/nekitdev/gd.py/blob/main/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/nekitdev/gd.py/blob/main/CONTRIBUTING.md
[Security]: https://github.com/nekitdev/gd.py/blob/main/SECURITY.md

[License]: https://github.com/nekitdev/gd.py/blob/main/LICENSE

[Package]: https://pypi.org/project/gd.py
[Coverage]: https://codecov.io/gh/nekitdev/gd.py
[Documentation]: https://nekitdev.github.io/gd.py

[Discord Badge]: https://img.shields.io/badge/chat-discord-5865f2
[License Badge]: https://img.shields.io/pypi/l/gd.py
[Version Badge]: https://img.shields.io/pypi/v/gd.py
[Downloads Badge]: https://img.shields.io/pypi/dm/gd.py

[Documentation Badge]: https://github.com/nekitdev/gd.py/workflows/docs/badge.svg
[Check Badge]: https://github.com/nekitdev/gd.py/workflows/check/badge.svg
[Test Badge]: https://github.com/nekitdev/gd.py/workflows/test/badge.svg
[Coverage Badge]: https://codecov.io/gh/nekitdev/gd.py/branch/main/graph/badge.svg

