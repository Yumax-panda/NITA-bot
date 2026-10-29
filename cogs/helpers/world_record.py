from __future__ import annotations

from dataclasses import dataclass

__all__ = ("WorldRecord",)


@dataclass(frozen=True, slots=True)
class WorldRecord:
    time_ms: int
    player_name: str | None = None
    proof_url: str | None = None
