from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from error import BotError
from mkworld.game_data.tracks import Track
from utils.time import input_text_to_time_ms

if TYPE_CHECKING:
    from bot import Bot


class TrackConverter(commands.Converter[Track]):
    async def convert(self, _: commands.Context[Bot], argument: str) -> Track:
        track = Track.from_nick(argument)

        if track is None:
            raise BotError(f"入力: {argument}に該当するコースが見つかりませんでした．")

        return track


class TimeMsConverter(commands.Converter[int]):
    async def convert(self, _: commands.Context[Bot], argument: str) -> int:
        time_ms = input_text_to_time_ms(argument)

        if time_ms is None:
            raise BotError(
                f"入力: {argument}は不正です."
                "1:40.123の場合, 140123のように入力してください."
            )

        return time_ms
