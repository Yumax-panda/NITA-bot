from __future__ import annotations

from enum import Enum

__all__ = ("Game",)


class Game(Enum):
    MKWORLD = (
        "mkworld",
        "マリオカートワールド",
        "Mario Kart World",
        "World",
        "https://raw.githubusercontent.com/Yumax-panda/MKWorld/refs/heads/main/tracks/{id}.webp",
    )
    MK8DX = (
        "mk8dx",
        "マリオカート8 デラックス",
        "Mario Kart 8 Deluxe",
        "8DX",
        "https://raw.githubusercontent.com/Yumax-panda/MK8DX/refs/heads/main/tracks/{id}.webp",
    )

    @property
    def slug(self) -> str:
        return self.value[0]

    @property
    def ja(self) -> str:
        return self.value[1]

    @property
    def en(self) -> str:
        return self.value[2]

    @property
    def short(self) -> str:
        return self.value[3]

    @property
    def image_base(self) -> str:
        return self.value[4]

    def image_url(self, track_id: str) -> str:
        return self.image_base.format(id=track_id)

    @staticmethod
    def from_slug(slug: str) -> Game | None:
        for game in Game:
            if game.slug == slug:
                return game
        return None

    @staticmethod
    def from_input(text: str) -> Game | None:
        key = text.lower().strip()
        mapping = {
            "mkworld": Game.MKWORLD,
            "world": Game.MKWORLD,
            "mkw": Game.MKWORLD,
            "w": Game.MKWORLD,
            "ワールド": Game.MKWORLD,
            "mk8dx": Game.MK8DX,
            "8dx": Game.MK8DX,
            "8": Game.MK8DX,
            "mk8": Game.MK8DX,
            "deluxe": Game.MK8DX,
            "dx": Game.MK8DX,
            "デラックス": Game.MK8DX,
        }
        return mapping.get(key)
