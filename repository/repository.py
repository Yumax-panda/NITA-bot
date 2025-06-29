from __future__ import annotations

import ssl
from typing import TYPE_CHECKING

from sqlalchemy import asc, func, select, tuple_
from sqlalchemy.ext.asyncio import create_async_engine

from model.core import metadata
from model.time_trials import TimeTrialData, time_trials

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

    from mkworld.game_data.tracks import Track

__all__ = ("get_repository", "Repository")


def get_repository(
    user: str,
    password: str,
    host_name: str,
    port: int,
    db_name: str,
    ssl_ca_path: str | None = None,
) -> Repository:
    dsn = f"mysql+aiomysql://{user}:{password}@{host_name}:{port}/{db_name}"

    if ssl_ca_path:
        ssl_context = ssl.create_default_context(cafile=ssl_ca_path)
        engine = create_async_engine(
            dsn,
            echo=True,
            pool_pre_ping=True,
            connect_args={"ssl": ssl_context},
        )
    else:
        engine = create_async_engine(
            dsn,
            echo=True,
            pool_pre_ping=True,
        )

    return Repository(engine)


class Repository:
    __slots__ = ("engine",)

    if TYPE_CHECKING:
        engine: AsyncEngine

    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def sync(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def create_time_trial(
        self, user_discord_id: str, track: Track, time_ms: int
    ) -> None:
        query = time_trials.insert().values(
            user_discord_id=user_discord_id,
            track=track.id,
            time_ms=time_ms,
        )

        async with self.engine.connect() as conn, conn.begin() as tx:
            try:
                await conn.execute(query)
                await tx.commit()

            except Exception as e:
                await tx.rollback()
                raise e

    async def get_leader_board(
        self, user_discord_ids: list[str], track: Track
    ) -> list[TimeTrialData]:
        """指定したユーザーの最新タイムを取得する．

        Parameters
        ----------
        user_discord_ids : list[str]
            取得したいユーザーのdiscord ID.
        track : Track
            コース．

        Returns
        -------
        list[TimeTrialData]
            タイムアタックのデータ．
        """
        sub_query = (
            select(
                time_trials.c.user_discord_id,
                func.max(time_trials.c.created_at).label("max_created_at"),
            )
            .where(
                time_trials.c.user_discord_id.in_(user_discord_ids),
                time_trials.c.track == track.id,
            )
            .group_by(time_trials.c.user_discord_id)
            .subquery()
        )

        query = (
            time_trials.select()
            .join(
                sub_query,
                tuple_(time_trials.c.user_discord_id, time_trials.c.created_at)
                == tuple_(sub_query.c.user_discord_id, sub_query.c.max_created_at),
            )
            .where(time_trials.c.track == track.id)
        )

        async with self.engine.connect() as conn:
            result = await conn.execute(query)

        ret: list[TimeTrialData] = []

        for data in result.fetchall():
            ret.append(
                TimeTrialData(
                    id=data.id,
                    user_discord_id=data.user_discord_id,
                    track=data.track,
                    time_ms=data.time_ms,
                    created_at=data.created_at,
                    updated_at=data.updated_at,
                )
            )
        return ret

    async def get_time_trial_history(
        self, user_discord_id: str, track: Track
    ) -> list[TimeTrialData]:
        query = (
            time_trials.select()
            .where(
                time_trials.c.track == track.id,
                time_trials.c.user_discord_id == user_discord_id,
            )
            .order_by(asc(time_trials.c.created_at))
        )

        async with self.engine.connect() as conn:
            result = await conn.execute(query)

        ret: list[TimeTrialData] = []

        for data in result.fetchall():
            ret.append(
                TimeTrialData(
                    id=data.id,
                    user_discord_id=data.user_discord_id,
                    track=data.track,
                    time_ms=data.time_ms,
                    created_at=data.created_at,
                    updated_at=data.updated_at,
                )
            )
        return ret
