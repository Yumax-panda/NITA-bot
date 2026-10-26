from __future__ import annotations

from .game import Game
from .mk8dx import Track as MK8DXTrack
from .mkworld import Track as MKWorldTrack

__all__ = (
    "Game",
    "Track",
    "MKWorldTrack",
    "MK8DXTrack",
    "track_class",
    "all_tracks",
    "find_tracks",
    "search_tracks",
)

type Track = MKWorldTrack | MK8DXTrack

TRACK_CLASSES: dict[Game, type[MKWorldTrack] | type[MK8DXTrack]] = {
    Game.MKWORLD: MKWorldTrack,
    Game.MK8DX: MK8DXTrack,
}


def track_class(game: Game) -> type[MKWorldTrack] | type[MK8DXTrack]:
    return TRACK_CLASSES[game]


def all_tracks(game: Game) -> list[Track]:
    return list(TRACK_CLASSES[game])


def find_tracks(nick: str) -> list[tuple[Game, Track]]:
    found: list[tuple[Game, Track]] = []
    for game, cls in TRACK_CLASSES.items():
        track = cls.from_nick(nick)
        if track is not None:
            found.append((game, track))
    return found


def search_tracks(nick: str) -> list[tuple[Game, Track]]:
    found: list[tuple[Game, Track]] = []
    for game, cls in TRACK_CLASSES.items():
        for track in cls.search(nick):
            found.append((game, track))
    return found
