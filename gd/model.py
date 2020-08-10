from gd.model_backend import (
    FloatField,
    IntField,
    StrField,
    URLField,
    IndexParser,
    Model,
)

__all__ = (
    "AbstractUserModel",
    "LoginIDModel",
    "SongModel",
)


class SongModel(Model):
    PARSER = IndexParser("~|~", map_like=True)

    id: int = IntField(index=1, default=0)
    name: str = StrField(index=2, default="unknown")
    author_id: int = IntField(index=3, default=0)
    author: str = StrField(index=4, default="unknown")
    size: float = FloatField(index=5, default=0.0)
    youtube_video_id: str = StrField(index=6, default="")
    youtube_channel_id: str = StrField(index=7, default="")
    # index 8 does not appear
    index_9: int = IntField(index=9, default=0)
    download_link: str = URLField(index=10, default="")


class LoginIDModel(Model):
    PARSER = IndexParser(",", map_like=False)

    account_id: int = IntField(index=0, default=0)
    id: int = IntField(index=1, default=0)


class AbstractUserModel(Model):
    PARSER = IndexParser(":", map_like=False)

    id: int = IntField(index=0, default=0)
    name: str = StrField(index=1, default="unknown")
    account_id: int = IntField(index=2, default=0)
