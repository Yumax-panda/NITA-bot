from __future__ import annotations

from unittest.mock import MagicMock

import aiohttp
import pytest

from cogs.time_trial import TimeTrial, WorldRecord
from game_data import MK8DXTrack, all_tracks
from game_data.game import Game


def _make_cog(get: MagicMock) -> TimeTrial:
    cog = TimeTrial.__new__(TimeTrial)
    cog.bot = MagicMock()
    cog.bot.session.get = get
    return cog


@pytest.mark.parametrize(
    "error", [TimeoutError(), aiohttp.ClientConnectionError("down")]
)
async def test_fetch_wr_returns_none_on_request_failure(error: BaseException) -> None:
    get = MagicMock(side_effect=error)
    cog = _make_cog(get)
    track = all_tracks(Game.MKWORLD)[0]

    assert await cog.fetch_mkworld_wr(track) is None
    get.assert_called_once()
    assert get.call_args.kwargs["params"] == {
        "game": track.game.id,
        "track": track.id,
    }


async def test_fetch_wr_returns_mk8dx_record_without_request() -> None:
    get = MagicMock()
    cog = _make_cog(get)
    record = WorldRecord(time_ms=98538, player_name="test_player")
    cog._mk8dx_wrs = {MK8DXTrack.MKS.id: record}

    assert await cog.fetch_wr(MK8DXTrack.MKS) == record
    assert await cog.fetch_wr(MK8DXTrack.WP) is None
    get.assert_not_called()


async def test_refresh_mk8dx_wrs_keeps_records_on_request_failure() -> None:
    cog = _make_cog(MagicMock(side_effect=TimeoutError()))
    records = {MK8DXTrack.MKS.id: WorldRecord(time_ms=98538)}
    cog._mk8dx_wrs = records

    await cog.refresh_mk8dx_wrs()

    assert cog._mk8dx_wrs is records
