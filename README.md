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

**Python 3.8 or above is required.**

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
"gd.py" = "^2.0.0-dev.0"
```

Alternatively, you can add it directly from the source:

```toml
[tool.poetry.dependencies."gd.py"]
git = "https://github.com/nekitdev/gd.py.git"
```

## Examples

### Interactive

![Song][Song]

### Fetching

```python
# file.py

from entrypoint import entrypoint

import gd

SONG_ID = 1081309

SONG_INFO = "`{song.name}` by `{song.artist.name}` (ID: `{song.id}`, size: `{song.size} MB`)"
song_info = SONG_INFO.format


async def async_main() -> None:
    song = await client.get_song(SONG_ID)

    print(song_info(song=song))


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
```

```console
$ python file.py
`PANDA EYES - BROKEN` by `PandaEyesOfficial` (ID: `1081309`, size: `9.71 MB`)
```

### Login

`gd.py` is now using hashed passwords for safety reasons.

[`gd.hash_password`][gd.encoding.hash_password] is provided for convenience.

Moreover, [`client.login`][gd.client.Client.login] returns an awaitable asynchronous context
manager, which can be utilized to factor out the blocks that require logging in.

In the snippet below we define the credentials and hash the password.

```python
import gd

client = gd.Client()

name = "name"
password = "********"

hashed_password = gd.hash_password(password)
```

Regular login:

```python
await client.login(name, hashed_password)

...  # the client is now logged in
```

Advanced version:

```python
async with client.login(name, hashed_password):
    ...  # the client is logged in here

...  # but not outside of the `async with` block!
```

### Listening

```python
from entrypoint import entrypoint

import gd

client = gd.Client()

DAILY_INFO = "new daily! `{daily.name}` by `{daily.creator.name}` (ID: `{daily.id}`)"
daily_info = DAILY_INFO.format


@client.event
async def on_daily(daily: gd.Level) -> None:
    print(daily_info(daily=daily))


client.listen_for_daily()


@entrypoint(__name__)
def main() -> None:
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

[Song]: https://github.com/nekitdev/gd.py/blob/main/assets/song.svg?raw=true

[gd.client.Client.login]: https://nekitdev.github.io/gd.py/reference/client#gd.client.Client.login
[gd.encoding.hash_password]: https://nekitdev.github.io/gd.py/reference/encoding#gd.encoding.hash_password
