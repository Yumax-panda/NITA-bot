from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Annotated

from discord import Color, Embed, app_commands, utils
from discord.ext import commands, tasks

from error import BotError
from game_data import Game, Track, track_class
from utils.base_model import BaseModel
from utils.time import display_time, format_time_diff

from .helpers.autocomplete import track_autocomplete
from .helpers.converter import TimeMsConverter, TrackConverter
from .helpers.paginator import EmbedPaginator, Paginator
from .utils import GroupCog

if TYPE_CHECKING:
    from bot import Bot

MKC_API = "https://mkcentral.com/api"


# ref: https://github.com/MarioKartCentral/MarioKartCentral/blob/main/src/backend/common/data/models/time_trials_api.py
@dataclass(frozen=True)
class ProofResponseData(BaseModel):
    id: str
    url: str
    type: str
    created_at: str
    status: str | None = "unvalidated"
    validator_id: int | None = None
    validated_at: str | None = None


@dataclass(frozen=True, slots=True)
class TimeTrialResponseData(BaseModel):
    id: str
    version: int
    player_id: int
    game: str
    track: str
    time_ms: int
    proofs: list[ProofResponseData]
    created_at: str
    updated_at: str
    validation_status: str = "proofless"
    player_name: str | None = None
    player_country_code: str | None = None


@dataclass(frozen=True, slots=True)
class LeaderboardResponseData(BaseModel):
    records: list[TimeTrialResponseData]


logger = logging.getLogger(__name__)


# TODO
class TimeTrial(GroupCog, name="NITA", description="NITA関連", group_name="nita"):
    if TYPE_CHECKING:
        _wr_cache: dict[str, TimeTrialResponseData]

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self._wr_cache = {}
        self.cleanup_cache.start()

    @commands.hybrid_command(
        name="game",
        description="使用するゲームを設定する.",
        usage="[world|8dx]",
    )
    @app_commands.describe(game="world または 8dx (省略で現在の設定を表示)")
    @app_commands.choices(
        game=[
            app_commands.Choice(name=Game.MKWORLD.ja, value=Game.MKWORLD.id),
            app_commands.Choice(name=Game.MK8DX.ja, value=Game.MK8DX.id),
        ]
    )
    async def set_game(
        self, ctx: commands.Context[Bot], game: str | None = None
    ) -> None:
        await ctx.defer()
        user_discord_id = str(ctx.author.id)

        if game is None:
            current = await self.repo.get_user_game(user_discord_id)
            await ctx.send(f"現在の設定: **{current.ja}**")
            return

        parsed = Game.from_input(game)

        if parsed is None:
            raise BotError(
                f"入力: {game}に該当するゲームが見つかりませんでした．"
                "`world`または`8dx`を指定してください．"
            )

        await self.repo.set_user_game(user_discord_id, parsed)
        await ctx.send(f"ゲームを**{parsed.ja}**に設定しました.")

    @commands.hybrid_command(
        aliases=["s"],
        description="タイムを記録する.",
        usage="<コース名> <タイム>",
    )
    @app_commands.describe(track="例: トロフィーシティ", time_ms="例: 140123")
    @app_commands.autocomplete(track=track_autocomplete)
    @app_commands.rename(time_ms="time")
    async def submit(
        self,
        ctx: commands.Context[Bot],
        track: Annotated[Track, TrackConverter],
        time_ms: Annotated[int, TimeMsConverter],
    ) -> None:
        await ctx.defer()
        user_discord_id = str(ctx.author.id)

        previous_pb = await self.repo.get_personal_best(
            user_discord_id=user_discord_id, track=track
        )
        wr = await self.fetch_wr(track)
        is_pb = previous_pb is None or time_ms < previous_pb.time_ms

        e = Embed(title=track.ja, color=Color.green())
        e.set_thumbnail(url=track.image_url)

        input_value = f"> {display_time(time_ms)}"
        if wr is not None:
            input_value += f" (WR {format_time_diff(time_ms - wr.time_ms)})"
        e.add_field(name="Input Time", value=input_value, inline=False)

        if previous_pb is None:
            e.add_field(name="Your Record", value="-", inline=False)
        else:
            pb_value = f"> {display_time(previous_pb.time_ms)}"
            if wr is not None:
                pb_value += (
                    f" (WR {format_time_diff(previous_pb.time_ms - wr.time_ms)})"
                )
            e.add_field(name="Your Record", value=pb_value, inline=False)

        if is_pb:
            await self.repo.create_time_trial(
                user_discord_id=user_discord_id,
                track=track,
                time_ms=time_ms,
            )
            e.set_footer(text=f"☑️ Updated by {ctx.author.name}")

        await ctx.send(embed=e)

    @commands.hybrid_command(
        aliases=["t", "show"],
        description="指定したコースのタイムを表示する.",
        usage="<コース名>",
    )
    @app_commands.describe(track="例: トロフィーシティ")
    @app_commands.autocomplete(track=track_autocomplete)
    @commands.guild_only()
    @app_commands.guild_only()
    async def ranking(
        self, ctx: commands.Context[Bot], track: Annotated[Track, TrackConverter]
    ) -> None:
        await ctx.defer()

        # guild_onlyによりctx.guildはNoneにはなりえない．
        if ctx.guild is None:
            return

        data = await self.repo.get_leader_board(
            user_discord_ids=list(map(lambda m: str(m.id), ctx.guild.members)),
            track=track,
        )

        if not data:
            raise BotError(f"{track.ja}はまだタイムが記録されていません.")

        sorted_data = sorted(data, key=lambda x: x.time_ms)

        template = Embed(title=track.ja, color=Color.green())
        template.set_thumbnail(url=track.image_url)
        paginator = EmbedPaginator(template=template)
        wr = await self.fetch_wr(track)

        for i, record in enumerate(sorted_data):
            prefix = f"{i + 1}."

            if i == 0:
                prefix = "🥇"
            elif i == 1:
                prefix = "🥈"
            elif i == 2:
                prefix = "🥉"

            value = f"> {display_time(record.time_ms)}"

            if wr is not None:
                diff = record.time_ms - wr.time_ms
                value += f" (WR {format_time_diff(diff)})"

            user = ctx.guild.get_member(int(record.user_discord_id))
            user_name = user.display_name if user is not None else "N/A"

            paginator.add_field(name=f"{prefix} {user_name}", value=value, inline=False)

        avg_time_ms = round(sum(record.time_ms for record in data) / len(data))
        avg_value = f"> {display_time(avg_time_ms)}"

        if wr is not None:
            avg_value += f" (WR {format_time_diff(avg_time_ms - wr.time_ms)})"

        paginator.add_field(name="Avg. Time", value=avg_value, inline=False)

        await Paginator(pages=paginator.to_pages(), context=ctx).start()

    @commands.hybrid_command(
        aliases=["d"],
        description="指定したコースの直近の記録を削除する.",
        usage="<コース名>",
    )
    @app_commands.describe(track="例: トロフィーシティ")
    @app_commands.autocomplete(track=track_autocomplete)
    async def delete(
        self, ctx: commands.Context[Bot], track: Annotated[Track, TrackConverter]
    ) -> None:
        await ctx.defer()
        user_discord_id = str(ctx.author.id)

        deleted = await self.repo.delete_latest_time_trial(
            user_discord_id=user_discord_id, track=track
        )

        if deleted is None:
            raise BotError(f"{track.ja}の記録が見つかりませんでした.")

        title = track.ja
        e = Embed(
            title="直近の記録を削除しました",
            description=f"{title}: {display_time(deleted.time_ms)}",
            color=Color.red(),
        )
        e.set_thumbnail(url=track.image_url)
        await ctx.send(embed=e)

    @commands.hybrid_command(
        aliases=["da"],
        description="指定したコースの記録を全て削除する.",
        usage="<コース名>",
    )
    @app_commands.describe(track="例: トロフィーシティ")
    @app_commands.autocomplete(track=track_autocomplete)
    async def delete_all(
        self, ctx: commands.Context[Bot], track: Annotated[Track, TrackConverter]
    ) -> None:
        await ctx.defer()
        user_discord_id = str(ctx.author.id)

        success = await self.repo.delete_time_trial(
            user_discord_id=user_discord_id, track=track
        )

        if not success:
            raise BotError(f"{track.ja}の記録が見つかりませんでした.")

        e = Embed(
            title="記録を全て削除しました",
            description=f"{track.ja}の記録を全て削除しました.",
            color=Color.red(),
        )
        e.set_thumbnail(url=track.image_url)
        await ctx.send(embed=e)

    @commands.hybrid_command(
        aliases=["p"],
        description=(
            "自分の記録を表示する. コースを指定しない場合は全コースの記録を表示する."
        ),
        usage="[コース名]",
    )
    @app_commands.describe(track="例: トロフィーシティ (省略可)")
    @app_commands.autocomplete(track=track_autocomplete)
    async def profile(
        self,
        ctx: commands.Context[Bot],
        track: Annotated[Track, TrackConverter] | None = None,
    ) -> None:
        await ctx.defer()
        user_discord_id = str(ctx.author.id)

        if track is not None:
            history = await self.repo.get_time_trial_history(
                user_discord_id=user_discord_id, track=track
            )

            if not history:
                raise BotError(f"{track.ja}の記録がありません.")

            pb = min(history, key=lambda x: x.time_ms)
            e = Embed(title=track.ja, color=Color.blue())
            e.set_thumbnail(url=track.image_url)
            e.set_footer(text=f"{ctx.author.display_name}'s Record")

            pb_value = f"> {display_time(pb.time_ms)}"
            wr = await self.fetch_wr(track)

            if wr is not None:
                diff_ms = pb.time_ms - wr.time_ms
                pb_value += f" (WR {format_time_diff(diff_ms)})"

            e.add_field(name="Your Record", value=pb_value, inline=False)

            if wr is not None:
                wr_value = f"{display_time(wr.time_ms)} (By {wr.player_name or 'N/A'})"
                wr_link = wr.proofs[0].url if wr.proofs else None

                if wr_link is not None:
                    wr_value = f"[{wr_value}]({wr_link})"

                e.add_field(name="WR", value=f"> {wr_value}", inline=False)

            recent = history[-5:][::-1]  # 新しい順
            if recent:
                recent_lines = []
                for record in recent:
                    time_str = display_time(record.time_ms)
                    diff = record.time_ms - pb.time_ms
                    diff_str = f" ({format_time_diff(diff)})"
                    recent_lines.append(f"> {time_str}{diff_str}")

                e.add_field(
                    name=f"最近の記録 (全{len(history)}件)",
                    value="\n".join(recent_lines),
                    inline=False,
                )

            await ctx.send(embed=e)

        else:
            records = await self.repo.get_user_records(user_discord_id=user_discord_id)

            if not records:
                raise BotError("まだ記録がありません.")

            template = Embed(
                title=f"{ctx.author.display_name}'s Records", color=Color.blue()
            )
            paginator = EmbedPaginator(template=template)

            diff_sum_ms = 0
            diff_count = 0

            for record in records:
                game = Game.from_id(record.game)

                if game is None:
                    continue

                track_obj = track_class(game).from_id(record.track)

                if track_obj is None:
                    continue

                value = f"> {display_time(record.time_ms)}"
                wr = await self.fetch_wr(track_obj)

                if wr is not None:
                    diff = record.time_ms - wr.time_ms
                    diff_sum_ms += diff
                    diff_count += 1
                    value += f" (WR {format_time_diff(diff)})"

                paginator.add_field(
                    name=track_obj.ja,
                    value=value,
                    inline=False,
                )

            if diff_count > 0:
                avg_diff = diff_sum_ms / diff_count / 1000
                paginator.add_field(
                    name="Avg. Diff.",
                    value=f"> {avg_diff:.3f} ({diff_count} tracks)",
                    inline=False,
                )

            await Paginator(pages=paginator.to_pages(), context=ctx).start()

    @commands.hybrid_command(
        name="today",
        description="直近24時間で更新した記録を表示する.",
    )
    async def today(self, ctx: commands.Context[Bot]) -> None:
        await ctx.defer()
        user_discord_id = str(ctx.author.id)

        records = await self.repo.get_recently_updated_records(
            user_discord_id=user_discord_id
        )

        if not records:
            raise BotError("直近24時間で更新した記録がありません.")

        now = datetime.now().astimezone()
        since = now - timedelta(hours=24)

        template = Embed(
            title="Daily Records",
            description=f"{utils.format_dt(since, 's')}~{utils.format_dt(now, 's')}",
            color=Color.green(),
        )
        template.set_footer(
            text=str(ctx.author), icon_url=ctx.author.display_avatar.url
        )
        paginator = EmbedPaginator(template=template)

        latest_before = await self.repo.get_latest_before_24h(
            user_discord_id=user_discord_id
        )

        grouped: dict[tuple[str, str], list[int]] = {}
        for record in records:
            grouped.setdefault((record.game, record.track), []).append(record.time_ms)

        for (game_slug, track_nick), time_ms_list in grouped.items():
            game = Game.from_id(game_slug)

            if game is None:
                continue

            track_obj = track_class(game).from_id(track_nick)

            if track_obj is None:
                continue

            latest = time_ms_list[0]
            baseline = latest_before.get((game_slug, track_nick))

            if baseline is None:
                value = f"> {display_time(latest)} (New)"
            else:
                diff = format_time_diff(latest - baseline)
                value = f"> {display_time(baseline)} -> {display_time(latest)} ({diff})"

            paginator.add_field(
                name=track_obj.ja,
                value=value,
                inline=False,
            )

        await Paginator(pages=paginator.to_pages(), context=ctx).start()

    async def fetch_wr(self, track: Track) -> TimeTrialResponseData | None:
        key = f"{track.game.id}:{track.id}"
        try:
            return self._wr_cache[key]
        except KeyError:
            wr = await self.fetch_wr_without_cache(track)
            if wr is not None:
                self._wr_cache[key] = wr
                return wr
        return None

    async def fetch_wr_without_cache(
        self, track: Track
    ) -> TimeTrialResponseData | None:
        url = f"{MKC_API}/time-trials/leaderboard?game={track.game.id}&track={track.id}"

        async with self.bot.session.get(url) as resp:
            if resp.ok:
                payload = await resp.json()
                data = LeaderboardResponseData.from_dict(payload)

                if not data.records:
                    logger.info(f"Track: {track.ja} has no WR.")
                    return None

                return data.records[0]
            else:
                logger.error(f"API {url}(GET) returned {resp.status}.")
                return None

    @tasks.loop(hours=1.0)
    async def cleanup_cache(self) -> None:
        self._wr_cache.clear()
        self.repo.clear_game_cache()


async def setup(bot: Bot) -> None:
    await bot.add_cog(TimeTrial(bot))
