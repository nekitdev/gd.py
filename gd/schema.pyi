from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import ContextManager, Generic, Literal, Optional, TypeVar

T = TypeVar("T")

class OptionSchema(Generic[T]):
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[OptionReader[T]]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> OptionReader[T]: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> OptionReader[T]: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> OptionReader[T]: ...
    @classmethod
    def new_message(cls) -> OptionBuilder[T]: ...

class OptionReader(Generic[T]):
    some: T
    none: None

    def which(self) -> Literal["some", "none"]: ...
    def as_builder(self) -> OptionBuilder[T]: ...

class OptionBuilder(Generic[T]):
    some: T
    none: None

    def which(self) -> Literal["some", "none"]: ...
    def copy(self) -> OptionBuilder[T]: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> OptionReader[T]: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class EitherRecordSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[EitherRecordReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> EitherRecordReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> EitherRecordReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> EitherRecordReader: ...
    @classmethod
    def new_message(cls) -> EitherRecordBuilder: ...

class EitherRecordReader:
    regular: int
    platformer: int

    def which(self) -> Literal["regular", "platformer"]: ...
    def as_builder(self) -> EitherRecordBuilder: ...

class EitherRecordBuilder:
    regular: int
    platformer: int

    def which(self) -> Literal["regular", "platformer"]: ...
    def copy(self) -> EitherRecordBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> EitherRecordReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class ArtistSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[ArtistReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ArtistReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> ArtistReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> ArtistReader: ...
    @classmethod
    def new_message(cls) -> ArtistBuilder: ...

class ArtistReader:
    id: int
    name: str
    verified: bool

    def as_builder(self) -> ArtistBuilder: ...

class ArtistBuilder:
    id: int
    name: str
    verified: bool

    def copy(self) -> ArtistBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> ArtistReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class SongReferenceSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[SongReferenceReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> SongReferenceReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> SongReferenceReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> SongReferenceReader: ...
    @classmethod
    def new_message(cls) -> SongReferenceBuilder: ...

class SongReferenceReader:
    id: int
    custom: bool

    def as_builder(self) -> SongReferenceBuilder: ...

class SongReferenceBuilder:
    id: int
    custom: bool

    def copy(self) -> SongReferenceBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> SongReferenceReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class SongSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[SongReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> SongReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> SongReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> SongReader: ...
    @classmethod
    def new_message(cls) -> SongBuilder: ...

class SongReader(SongSchema):
    id: int
    name: str
    artist: ArtistReader
    size: float
    url: OptionReader[str]

    def as_builder(self) -> SongBuilder: ...

class SongBuilder(SongSchema):
    id: int
    name: str
    artist: ArtistBuilder
    size: float
    url: OptionBuilder[str]

    def copy(self) -> SongBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> SongReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class UserReferenceSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[UserReferenceReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> UserReferenceReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> UserReferenceReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> UserReferenceReader: ...
    @classmethod
    def new_message(cls) -> UserReferenceBuilder: ...

class UserReferenceReader:
    id: int
    name: str
    accountId: int

    def as_builder(self) -> UserReferenceBuilder: ...

class UserReferenceBuilder:
    id: int
    name: str
    accountId: int

    def copy(self) -> UserReferenceBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> UserReferenceReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class UserStatisticsSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[UserStatisticsReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> UserStatisticsReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> UserStatisticsReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> UserStatisticsReader: ...
    @classmethod
    def new_message(cls) -> UserStatisticsBuilder: ...

class UserStatisticsReader:
    stars: int
    moons: int
    demons: int
    diamonds: int
    userCoins: int
    secretCoins: int
    creatorPoints: int
    rank: int

    def as_builder(self) -> UserStatisticsBuilder: ...

class UserStatisticsBuilder:
    stars: int
    moons: int
    demons: int
    diamonds: int
    userCoins: int
    secretCoins: int
    creatorPoints: int
    rank: int

    def copy(self) -> UserStatisticsBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> UserStatisticsReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class UserCosmeticsSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[UserCosmeticsReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> UserCosmeticsReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> UserCosmeticsReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> UserCosmeticsReader: ...
    @classmethod
    def new_message(cls) -> UserCosmeticsBuilder: ...

class UserCosmeticsReader:
    color1Id: int
    color2Id: int
    color3Id: int
    glow: bool
    iconType: int
    iconId: int
    cubeId: int
    shipId: int
    ballId: int
    ufoId: int
    waveId: int
    robotId: int
    spiderId: int
    swingId: int
    jetpackId: int
    explosionId: int
    streakId: int

    def as_builder(self) -> UserCosmeticsBuilder: ...

class UserCosmeticsBuilder:
    color1Id: int
    color2Id: int
    color3Id: int
    glow: bool
    iconType: int
    iconId: int
    cubeId: int
    shipId: int
    ballId: int
    ufoId: int
    waveId: int
    robotId: int
    spiderId: int
    swingId: int
    jetpackId: int
    explosionId: int
    streakId: int

    def copy(self) -> UserCosmeticsBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> UserCosmeticsReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class UserStatesSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[UserStatesReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> UserStatesReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> UserStatesReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> UserStatesReader: ...
    @classmethod
    def new_message(cls) -> UserStatesBuilder: ...

class UserStatesReader:
    messageState: int
    friendRequestState: int
    commentState: int
    friendState: int

    def as_builder(self) -> UserStatesBuilder: ...

class UserStatesBuilder:
    messageState: int
    friendRequestState: int
    commentState: int
    friendState: int

    def copy(self) -> UserStatesBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> UserStatesReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class UserSocialsSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[UserSocialsReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> UserSocialsReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> UserSocialsReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> UserSocialsReader: ...
    @classmethod
    def new_message(cls) -> UserSocialsBuilder: ...

class UserSocialsReader:
    youtube: OptionReader[str]
    x: OptionReader[str]
    twitch: OptionReader[str]
    discord: OptionReader[str]

    def as_builder(self) -> UserSocialsBuilder: ...

class UserSocialsBuilder:
    youtube: OptionBuilder[str]
    x: OptionBuilder[str]
    twitch: OptionBuilder[str]
    discord: OptionBuilder[str]

    def copy(self) -> UserSocialsBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> UserSocialsReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class UserLeaderboardSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[UserLeaderboardReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> UserLeaderboardReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> UserLeaderboardReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> UserLeaderboardReader: ...
    @classmethod
    def new_message(cls) -> UserLeaderboardBuilder: ...

class UserSchema:
    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> ContextManager[UserReader]: ...
    @classmethod
    def from_bytes_packed(
        cls,
        data: bytes,
        traversal_limit_in_words: Optional[int] = ...,
        nesting_limit: Optional[int] = ...,
    ) -> UserReader: ...
    @classmethod
    def read(cls, reader: BufferedReader) -> UserReader: ...
    @classmethod
    def read_packed(cls, reader: BufferedReader) -> UserReader: ...
    @classmethod
    def new_message(cls) -> UserBuilder: ...

class UserLeaderboardReader:
    record: EitherRecordReader
    coins: int
    recordedAt: int

    def as_builder(self) -> UserLeaderboardBuilder: ...

class UserLeaderboardBuilder:
    record: EitherRecordBuilder
    coins: int
    recordedAt: int

    def copy(self) -> UserLeaderboardBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> UserLeaderboardReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...

class UserReader:
    id: int
    name: str
    accountId: int
    roleId: int
    banned: bool
    statistics: OptionReader[UserStatisticsReader]
    cosmetics: OptionReader[UserCosmeticsReader]
    states: OptionReader[UserStatesReader]
    socials: OptionReader[UserSocialsReader]
    place: OptionReader[int]
    leaderboard: OptionReader[UserLeaderboardReader]

    def as_builder(self) -> UserBuilder: ...

class UserBuilder:
    id: int
    name: str
    accountId: int
    roleId: int
    banned: bool
    statistics: OptionBuilder[UserStatisticsBuilder]
    cosmetics: OptionBuilder[UserCosmeticsBuilder]
    states: OptionBuilder[UserStatesBuilder]
    socials: OptionBuilder[UserSocialsBuilder]
    place: OptionBuilder[int]
    leaderboard: OptionBuilder[UserLeaderboardBuilder]

    def copy(self) -> UserBuilder: ...
    def to_bytes(self) -> bytes: ...
    def to_bytes_packed(self) -> bytes: ...
    def as_reader(self) -> UserReader: ...
    def write(self, writer: BufferedWriter) -> None: ...
    def write_packed(self, writer: BufferedWriter) -> None: ...
