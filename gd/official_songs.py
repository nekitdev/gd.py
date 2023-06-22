from typing import Type, TypeVar

from attrs import frozen

from gd.constants import DEFAULT_ID, EMPTY

__all__ = ("OfficialSong", "OFFICIAL_SONGS", "ID_TO_OFFICIAL_SONG", "NAME_TO_OFFICIAL_SONG")

OS = TypeVar("OS", bound="OfficialSong")


@frozen()
class OfficialSong:
    id: int
    name: str
    artist_name: str

    @classmethod
    def default(cls: Type[OS], id: int = DEFAULT_ID, name: str = EMPTY) -> OS:
        return cls(id=id, name=name, artist_name=EMPTY)


OFFICIAL_SONGS = (
    OfficialSong(id=0, name="Stereo Madness", artist_name="ForeverBound"),
    OfficialSong(id=1, name="Back On Track", artist_name="DJVI"),
    OfficialSong(id=2, name="Polargeist", artist_name="Step"),
    OfficialSong(id=3, name="Dry Out", artist_name="DJVI"),
    OfficialSong(id=4, name="Base After Base", artist_name="DJVI"),
    OfficialSong(id=5, name="Can't Let Go", artist_name="DJVI"),
    OfficialSong(id=6, name="Jumper", artist_name="Waterflame"),
    OfficialSong(id=7, name="Time Machine", artist_name="Waterflame"),
    OfficialSong(id=8, name="Cycles", artist_name="DJVI"),
    OfficialSong(id=9, name="xStep", artist_name="DJVI"),
    OfficialSong(id=10, name="Clutterfunk", artist_name="Waterflame"),
    OfficialSong(id=11, name="Theory of Everything", artist_name="DJ-Nate"),
    OfficialSong(id=12, name="Electroman Adventures", artist_name="Waterflame"),
    OfficialSong(id=13, name="Clubstep", artist_name="DJ-Nate"),
    OfficialSong(id=14, name="Electrodynamix", artist_name="DJ-Nate"),
    OfficialSong(id=15, name="Hexagon Force", artist_name="Waterflame"),
    OfficialSong(id=16, name="Blast Processing", artist_name="Waterflame"),
    OfficialSong(id=17, name="Theory of Everything 2", artist_name="DJ-Nate"),
    OfficialSong(id=18, name="Geometrical Dominator", artist_name="Waterflame"),
    OfficialSong(id=19, name="Deadlocked", artist_name="F-777"),
    OfficialSong(id=20, name="Fingerdash", artist_name="MDK"),
    OfficialSong(id=21, name="The Seven Seas", artist_name="F-777"),
    OfficialSong(id=22, name="Viking Arena", artist_name="F-777"),
    OfficialSong(id=23, name="Airborne Robots", artist_name="F-777"),
    OfficialSong(id=24, name="Secret", artist_name="RobTop"),
    OfficialSong(id=25, name="Payload", artist_name="Dex Arson"),
    OfficialSong(id=26, name="Beast Mode", artist_name="Dex Arson"),
    OfficialSong(id=27, name="Machina", artist_name="Dex Arson"),
    OfficialSong(id=28, name="Years", artist_name="Dex Arson"),
    OfficialSong(id=29, name="Frontlines", artist_name="Dex Arson"),
    OfficialSong(id=30, name="Space Pirates", artist_name="Waterflame"),
    OfficialSong(id=31, name="Striker", artist_name="Waterflame"),
    OfficialSong(id=32, name="Embers", artist_name="Dex Arson"),
    OfficialSong(id=33, name="Round 1", artist_name="Dex Arson"),
    OfficialSong(id=34, name="Monster Dance Off", artist_name="F-777"),
    OfficialSong(id=35, name="Press Start", artist_name="MDK"),
    OfficialSong(id=36, name="Nock Em", artist_name="Bossfight"),
    OfficialSong(id=37, name="Power Trip", artist_name="Boom Kitty"),
)

ID_TO_OFFICIAL_SONG = {official_song.id: official_song for official_song in OFFICIAL_SONGS}
NAME_TO_OFFICIAL_SONG = {official_song.name: official_song for official_song in OFFICIAL_SONGS}
