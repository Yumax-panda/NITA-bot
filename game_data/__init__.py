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
