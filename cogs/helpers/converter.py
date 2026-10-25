from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from error import BotError
from game_data import Game
from utils.time import input_text_to_time_ms

if TYPE_CHECKING:
    from bot import Bot


class GameConverter(commands.Converter[Game]):
    async def convert(self, _: commands.Context[Bot], argument: str) -> Game:
        game = Game.from_input(argument)

        if game is None:
            raise BotError(
                f"入力: {argument}に該当するゲームが見つかりませんでした．"
                "`world`または`8dx`を指定してください．"
            )

        return game


class TimeMsConverter(commands.Converter[int]):
    async def convert(self, _: commands.Context[Bot], argument: str) -> int:
        time_ms = input_text_to_time_ms(argument)

        if time_ms is None:
            raise BotError(
                f"入力: {argument}は正しくありません.\n"
                "1:40.123の場合, 140123のように入力してください."
            )

        return time_ms
