from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

    from .game import Game

__all__ = ("BaseTrack",)


class BaseTrack(Enum):
    @property
    def en(self) -> str:
        return self.value[0]

    @property
    def ja(self) -> str:
        return self.value[1]

    @property
    def aliases(self) -> set[str]:
        return {alias.lower() for alias in self.value[4]}

    @property
    def id(self) -> str:
        return self.value[2]

    @property
    def game(self) -> Game:
        raise NotImplementedError

    @property
    def image_url(self) -> str:
        return self.game.image_url(self.id)

    @classmethod
    def from_nick(cls, nick: str) -> Self | None:
        name = nick.lower()
        for track in cls:
            if name in track.aliases:
                return track
        return None

    @classmethod
    def from_id(cls, track_id: str) -> Self | None:
        for track in cls:
            if track.id == track_id:
                return track
        return None

    @classmethod
    def search(cls, nick: str) -> list[Self]:
        name = nick.lower()
        return [track for track in cls if any(name in alias for alias in track.aliases)]
