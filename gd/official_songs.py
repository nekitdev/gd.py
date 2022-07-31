from attrs import evolve, field, frozen

from gd.artist import Artist
from gd.constants import UNKNOWN

__all__ = (
    "OFFICIAL_CLIENT_SONGS", "OFFICIAL_SERVER_SONGS", "OfficialSong", "create_default_offical_song"
)


def create_artist(name: str = UNKNOWN) -> Artist:
    return Artist(name=name)


@frozen()
class OfficialSong:
    id: int = field(default=0)
    name: str = field(default=UNKNOWN)
    artist: Artist = field(factory=create_artist)


def create_default_offical_song(id: int = 0) -> OfficialSong:
    return OfficialSong(id=id)


OFFICIAL_CLIENT_SONGS = (
    OfficialSong(id=0, name="Stay Inside Me", artist=create_artist("OcularNebula")),
    OfficialSong(id=1, name="Stereo Madness", artist=create_artist("ForeverBound")),
    OfficialSong(id=2, name="Back On Track", artist=create_artist("DJVI")),
    OfficialSong(id=3, name="Polargeist", artist=create_artist("Step")),
    OfficialSong(id=4, name="Dry Out", artist=create_artist("DJVI")),
    OfficialSong(id=5, name="Base After Base", artist=create_artist("DJVI")),
    OfficialSong(id=6, name="Can't Let Go", artist=create_artist("DJVI")),
    OfficialSong(id=7, name="Jumper", artist=create_artist("Waterflame")),
    OfficialSong(id=8, name="Time Machine", artist=create_artist("Waterflame")),
    OfficialSong(id=9, name="Cycles", artist=create_artist("DJVI")),
    OfficialSong(id=10, name="xStep", artist=create_artist("DJVI")),
    OfficialSong(id=11, name="Clutterfunk", artist=create_artist("Waterflame")),
    OfficialSong(id=12, name="Theory of Everything", artist=create_artist("DJ-Nate")),
    OfficialSong(id=13, name="Electroman Adventures", artist=create_artist("Waterflame")),
    OfficialSong(id=14, name="Clubstep", artist=create_artist("DJ-Nate")),
    OfficialSong(id=15, name="Electrodynamix", artist=create_artist("DJ-Nate")),
    OfficialSong(id=16, name="Hexagon Force", artist=create_artist("Waterflame")),
    OfficialSong(id=17, name="Blast Processing", artist=create_artist("Waterflame")),
    OfficialSong(id=18, name="Theory of Everything 2", artist=create_artist("DJ-Nate")),
    OfficialSong(id=19, name="Geometrical Dominator", artist=create_artist("Waterflame")),
    OfficialSong(id=20, name="Deadlocked", artist=create_artist("F-777")),
    OfficialSong(id=21, name="Fingerdash", artist=create_artist("MDK")),
    OfficialSong(id=22, name="The Seven Seas", artist=create_artist("F-777")),
    OfficialSong(id=23, name="Viking Arena", artist=create_artist("F-777")),
    OfficialSong(id=24, name="Airborne Robots", artist=create_artist("F-777")),
    OfficialSong(id=25, name="Secret", artist=create_artist("RobTop")),
    OfficialSong(id=26, name="Payload", artist=create_artist("Dex Arson")),
    OfficialSong(id=27, name="Beast Mode", artist=create_artist("Dex Arson")),
    OfficialSong(id=28, name="Machina", artist=create_artist("Dex Arson")),
    OfficialSong(id=29, name="Years", artist=create_artist("Dex Arson")),
    OfficialSong(id=30, name="Frontlines", artist=create_artist("Dex Arson")),
    OfficialSong(id=31, name="Space Pirates", artist=create_artist("Waterflame")),
    OfficialSong(id=32, name="Striker", artist=create_artist("Waterflame")),
    OfficialSong(id=33, name="Embers", artist=create_artist("Dex Arson")),
    OfficialSong(id=34, name="Round 1", artist=create_artist("Dex Arson")),
    OfficialSong(id=35, name="Monster Dance Off", artist=create_artist("F-777")),
    OfficialSong(id=36, name="Press Start", artist=create_artist("MDK")),
    OfficialSong(id=37, name="Nock Em", artist=create_artist("Bossfight")),
    OfficialSong(id=38, name="Power Trip", artist=create_artist("Boom Kitty")),
)

OFFICIAL_SERVER_SONGS = tuple(
    evolve(official_song, id=official_song.id - 1) for official_song in OFFICIAL_CLIENT_SONGS
)
