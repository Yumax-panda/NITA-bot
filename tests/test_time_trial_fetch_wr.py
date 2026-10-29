from __future__ import annotations

from unittest.mock import MagicMock

import aiohttp
import pytest

from cogs.time_trial import TimeTrial
from game_data import all_tracks
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

    assert await cog.fetch_wr_without_cache(track) is None
    get.assert_called_once()
    assert get.call_args.kwargs["params"] == {
        "game": track.game.id,
        "track": track.id,
    }
