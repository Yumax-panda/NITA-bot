from pathlib import Path

import pytest

from cogs.time_trial import WorldRecord, parse_mk8dx_leaderboard
from game_data import Game, MK8DXTrack, all_tracks

SHEET = (Path(__file__).parent / "data" / "nita150.csv").read_text(encoding="utf-8")


def test_parse_mk8dx_leaderboard_covers_all_tracks() -> None:
    records = parse_mk8dx_leaderboard(SHEET)

    assert records.keys() == {track.id for track in all_tracks(Game.MK8DX)}


def test_parse_mk8dx_leaderboard_takes_first_place() -> None:
    records = parse_mk8dx_leaderboard(SHEET)

    assert records[MK8DXTrack.MKS.id] == WorldRecord(
        time_ms=98538, player_name="test_001"
    )
    assert records[MK8DXTrack.BCMO.id] == WorldRecord(
        time_ms=113617, player_name="test_002"
    )
    assert records[MK8DXTrack.BCMA.id] == WorldRecord(
        time_ms=103695, player_name="test_052"
    )
    assert records[MK8DXTrack.bRR.id] == WorldRecord(
        time_ms=152745, player_name="test_863"
    )


@pytest.mark.parametrize("time", ["1:45.118*", "1:45.118"])
def test_parse_mk8dx_leaderboard_accepts_time_with_asterisk(time: str) -> None:
    sheet = f"MKS,,,,,,Mario Kart Stadium\n,1,,test_player,{time},,\n"

    assert parse_mk8dx_leaderboard(sheet) == {
        MK8DXTrack.MKS.id: WorldRecord(time_ms=105118, player_name="test_player"),
    }
