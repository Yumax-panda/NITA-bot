from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from discord import app_commands
from discord.ext import commands

from mkworld.game_data.tracks import Track

from .helpers.autocomplete import query_track_autocomplete
from .helpers.converter import TimeMsConverter, TrackConverter
from .utils import Cog

if TYPE_CHECKING:
    from bot import Bot


# TODO
class TimeTrial(Cog, name="NITA", description="NITA関連"):
    @commands.hybrid_command(
        aliases=["s"],
        description="タイムを記録する.",
        usage="<コース名> <タイム>",
    )
    @app_commands.describe(track="例: トロフィーシティ", time_ms="例: 140123")
    @app_commands.autocomplete(track=query_track_autocomplete)
    @app_commands.rename(time_ms="time")  # プログラム内のパラメータ名と合わせるため
    async def submit(
        self,
        ctx: commands.Context[Bot],
        track: Annotated[Track, TrackConverter],
        time_ms: Annotated[int, TimeMsConverter],
    ) -> None:
        await ctx.defer()

        await self.repo.create_time_trial(
            user_discord_id=str(ctx.author.id),
            track=track,
            time_ms=time_ms,
        )
        await ctx.send(f"登録完了: {track}, time_ms: {time_ms}")

    @commands.hybrid_command(
        aliases=["t", "show"],
        description="指定したコースのタイムを表示する.",
        usage="<コース名>",
    )
    @app_commands.describe(track="例: トロフィーシティ")
    @app_commands.autocomplete(track=query_track_autocomplete)
    async def track(
        self, ctx: commands.Context[Bot], track: Annotated[Track, TrackConverter]
    ) -> None:
        await ctx.defer()
        data = await self.repo.get_leader_board(
            user_discord_ids=[str(ctx.author.id)], track=track
        )
        await ctx.send(f"data: {data}")


async def setup(bot: Bot) -> None:
    await bot.add_cog(TimeTrial(bot))
