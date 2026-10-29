from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from game_data import MK8DXTrack
from utils.time import display_time_to_ms

__all__ = (
    "WorldRecord",
    "parse_mk8dx_leaderboard",
)

_TRACK_COLUMN = 0
_RANK_COLUMN = 1
_PLAYER_COLUMN = 3
_TIME_COLUMN = 4

_SHEET_TRACK_IDS = {
    "bCMn": MK8DXTrack.BCMO.id,
    "bCMl": MK8DXTrack.BCMA.id,
    "bRRW": MK8DXTrack.bRR.id,
}


@dataclass(frozen=True, slots=True)
class WorldRecord:
    time_ms: int
    player_name: str | None = None
    proof_url: str | None = None


def parse_mk8dx_leaderboard(text: str) -> dict[str, WorldRecord]:
    """MK8DXのNITAリーダーボード(CSV)から, コースIDごとのWRを取得する."""
    records: dict[str, WorldRecord] = {}
    track: MK8DXTrack | None = None

    for row in csv.reader(io.StringIO(text)):
        if len(row) <= _TIME_COLUMN:
            continue

        if sheet_id := row[_TRACK_COLUMN].strip():
            track = MK8DXTrack.from_id(_SHEET_TRACK_IDS.get(sheet_id, sheet_id))
            continue

        if track is None or track.id in records or row[_RANK_COLUMN] != "1":
            continue

        time_ms = display_time_to_ms(row[_TIME_COLUMN].rstrip("*"))

        if time_ms is not None:
            records[track.id] = WorldRecord(
                time_ms=time_ms, player_name=row[_PLAYER_COLUMN].strip() or None
            )

    return records
