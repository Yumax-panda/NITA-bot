from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any

from discord import Color, Embed, app_commands
from discord.ext import commands, tasks

from mkworld.game_data.tracks import Track
from utils.time import display_time, format_time_diff

from .helpers.autocomplete import query_track_autocomplete
from .helpers.converter import TimeMsConverter, TrackConverter
from .utils import GroupCog

if TYPE_CHECKING:
    from bot import Bot

MKC_API = "https://mkcentral.com/api"


# ref: https://github.com/MarioKartCentral/MarioKartCentral/blob/main/src/backend/common/data/models/time_trials_api.py
@dataclass(frozen=True, slots=True)
class ProofResponseData:
    id: str
    url: str
    type: str
    created_at: str
    status: str | None = "unvalidated"
    validator_id: int | None = None
    validated_at: str | None = None


@dataclass(frozen=True, slots=True)
class TimeTrialResponseData:
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

    @staticmethod
    def from_dict(payload: dict) -> TimeTrialResponseData:
        proofs: list[dict[str, Any]] = payload.pop("proofs")
        return TimeTrialResponseData(
            **payload, proofs=list(map(lambda p: ProofResponseData(**p), proofs))
        )


@dataclass(frozen=True, slots=True)
class LeaderboardResponseData:
    records: list[TimeTrialResponseData]


logger = logging.getLogger(__name__)


# TODO
class TimeTrial(GroupCog, name="NITA", description="NITA関連", group_name="nita"):
    if TYPE_CHECKING:
        _wr_cache: dict[str, TimeTrialResponseData]

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self._wr_cache = {}
        self.cleanup_wr_cache.start()

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
        user_discord_id = str(ctx.author.id)

        await self.repo.create_time_trial(
            user_discord_id=user_discord_id,
            track=track,
            time_ms=time_ms,
        )

        history = await self.repo.get_time_trial_history(
            user_discord_id=user_discord_id, track=track
        )

        new_record = history[-1]
        e = Embed(title=track.name_ja, color=Color.green())

        new_record_brief = f"> {display_time(new_record.time_ms)}"
        wr = await self.fetch_wr(track)

        if wr is not None:
            diff_ms = new_record.time_ms - wr.time_ms
            new_record_brief += f" ({format_time_diff(diff_ms)})"

        e.add_field(name="New Record", value=new_record_brief, inline=False)
        e.set_footer(text=str(ctx.author), icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=e)

    @commands.hybrid_command(
        aliases=["t", "show"],
        description="指定したコースのタイムを表示する.",
        usage="<コース名>",
    )
    @app_commands.describe(track="例: トロフィーシティ")
    @app_commands.autocomplete(track=query_track_autocomplete)
    @commands.guild_only()
    @app_commands.guild_only()
    async def track(
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
        await ctx.send(f"data: {data}")

    async def fetch_wr(self, track: Track) -> TimeTrialResponseData | None:
        try:
            return self._wr_cache[track.abbr]
        except KeyError:
            wr = await self.fetch_wr_without_cache(track)
            if wr is not None:
                self._wr_cache[track.abbr] = wr
                return wr
        return None

    async def fetch_wr_without_cache(
        self, track: Track
    ) -> TimeTrialResponseData | None:
        url = f"{MKC_API}/time-trials/leaderboard?game=mkworld&track={track.abbr}"

        async with self.bot.session.get(url) as resp:
            if resp.ok:
                payload = await resp.json()
                data = LeaderboardResponseData(
                    records=list(
                        map(
                            lambda d: TimeTrialResponseData.from_dict(d),
                            payload["records"],
                        )
                    )
                )

                if not data.records:
                    logger.info(f"Track: {track.name} has no WR.")
                    return None

                return data.records[0]
            else:
                logger.error(f"API {url}(GET) returned {resp.status}.")
                return None

    @tasks.loop(hours=1.0)
    async def cleanup_wr_cache(self) -> None:
        self._wr_cache.clear()


async def setup(bot: Bot) -> None:
    await bot.add_cog(TimeTrial(bot))
