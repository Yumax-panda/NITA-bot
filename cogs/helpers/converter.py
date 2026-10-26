from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from error import BotError
from game_data import Game, track_class
from utils.time import input_text_to_time_ms

if TYPE_CHECKING:
    from bot import Bot
    from game_data import Track


class TrackConverter(commands.Converter["Track"]):
    async def convert(self, ctx: commands.Context[Bot], argument: str) -> Track:
        game = await ctx.bot.repo.get_user_game(str(ctx.author.id))
        cls = track_class(game)
        track = cls.from_id(argument) or cls.from_nick(argument)

        if track is None:
            raise BotError(
                f"入力: {argument}に該当するコースが{game.ja}では見つかりませんでした．"
            )

        return track


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
