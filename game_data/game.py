from __future__ import annotations

from enum import Enum

__all__ = ("Game",)


class Game(Enum):
    MKWORLD = (
        "mkworld",
        "マリオカートワールド",
        "Mario Kart World",
        "MKWorld",
        "https://raw.githubusercontent.com/Yumax-panda/MarioKart/refs/heads/main/{game}/tracks/{id}.webp",
    )
    MK8DX = (
        "mk8dx",
        "マリオカート8DX",
        "Mario Kart 8 Deluxe",
        "MK8DX",
        "https://raw.githubusercontent.com/Yumax-panda/MarioKart/refs/heads/main/{game}/tracks/{id}.png",
    )

    @property
    def id(self) -> str:
        return self.value[0]

    @property
    def ja(self) -> str:
        return self.value[1]

    @property
    def short(self) -> str:
        return self.value[3]

    @property
    def image_base(self) -> str:
        return self.value[4]

    def image_url(self, track_id: str) -> str:
        return self.image_base.format(game=self.id, id=track_id)

    @staticmethod
    def from_id(id: str) -> Game | None:
        for game in Game:
            if game.id == id:
                return game
        return None

    @staticmethod
    def from_input(text: str) -> Game | None:
        key = text.lower().strip()
        aliases = {
            Game.MKWORLD: ("mkworld", "world", "mkw", "w", "ワールド"),
            Game.MK8DX: ("mk8dx", "8dx", "8", "mk8", "deluxe", "dx", "デラックス"),
        }
        for game, keys in aliases.items():
            if key in keys:
                return game
        return None
