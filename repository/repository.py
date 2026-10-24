from __future__ import annotations

import ssl
from typing import TYPE_CHECKING

from sqlalchemy import asc, desc, func, select, text, tuple_
from sqlalchemy.engine import URL
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
    echo: bool = False,
) -> Repository:
    dsn = URL.create(
        "mysql+aiomysql",
        username=user,
        password=password,
        host=host_name,
        port=port,
        database=db_name,
    )

    if ssl_ca_path:
        ssl_context = ssl.create_default_context(cafile=ssl_ca_path)
        engine = create_async_engine(
            dsn,
            echo=echo,
            pool_pre_ping=True,
            connect_args={"ssl": ssl_context},
        )
    else:
        engine = create_async_engine(
            dsn,
            echo=echo,
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

    async def delete_time_trial(self, user_discord_id: str, track: Track) -> bool:
        """指定したユーザーのコースの記録を全て削除する．

        Parameters
        ----------
        user_discord_id : str
            ユーザーのDiscord ID.
        track : Track
            コース．

        Returns
        -------
        bool
            削除に成功したかどうか．
        """
        query = time_trials.delete().where(
            time_trials.c.user_discord_id == user_discord_id,
            time_trials.c.track == track.id,
        )

        async with self.engine.connect() as conn, conn.begin() as tx:
            try:
                result = await conn.execute(query)
                await tx.commit()
                return result.rowcount > 0
            except Exception as e:
                await tx.rollback()
                raise e

    async def delete_latest_time_trial(
        self, user_discord_id: str, track: Track
    ) -> TimeTrialData | None:
        """指定したユーザーのコースの直近1件の記録を削除する．

        Parameters
        ----------
        user_discord_id : str
            ユーザーのDiscord ID.
        track : Track
            コース．

        Returns
        -------
        TimeTrialData | None
            削除した記録．記録がない場合はNone．
        """
        select_query = (
            time_trials.select()
            .where(
                time_trials.c.user_discord_id == user_discord_id,
                time_trials.c.track == track.id,
            )
            .order_by(desc(time_trials.c.created_at), desc(time_trials.c.id))
            .limit(1)
        )

        async with self.engine.connect() as conn, conn.begin() as tx:
            try:
                result = await conn.execute(select_query)
                data = result.fetchone()

                if data is None:
                    await tx.rollback()
                    return None

                await conn.execute(
                    time_trials.delete().where(time_trials.c.id == data.id)
                )
                await tx.commit()

                return TimeTrialData(
                    id=data.id,
                    user_discord_id=data.user_discord_id,
                    track=data.track,
                    time_ms=data.time_ms,
                    created_at=data.created_at,
                    updated_at=data.updated_at,
                )
            except Exception as e:
                await tx.rollback()
                raise e

    async def get_user_records(self, user_discord_id: str) -> list[TimeTrialData]:
        """指定したユーザーの全コースの最速タイムを取得する．

        Parameters
        ----------
        user_discord_id : str
            ユーザーのDiscord ID.

        Returns
        -------
        list[TimeTrialData]
            各コースの最速タイム．
        """
        sub_query = (
            select(
                time_trials.c.track,
                func.min(time_trials.c.time_ms).label("min_time_ms"),
            )
            .where(time_trials.c.user_discord_id == user_discord_id)
            .group_by(time_trials.c.track)
            .subquery()
        )

        query = (
            time_trials.select()
            .join(
                sub_query,
                (time_trials.c.track == sub_query.c.track)
                & (time_trials.c.time_ms == sub_query.c.min_time_ms),
            )
            .where(time_trials.c.user_discord_id == user_discord_id)
            .order_by(asc(time_trials.c.track))
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

    async def get_recently_updated_records(
        self, user_discord_id: str
    ) -> list[TimeTrialData]:
        """直近24時間で更新したユーザーの記録を取得する．

        Parameters
        ----------
        user_discord_id : str
            ユーザーのDiscord ID.

        Returns
        -------
        list[TimeTrialData]
            直近24時間で更新した記録．更新が新しい順．
        """
        query = (
            time_trials.select()
            .where(
                time_trials.c.user_discord_id == user_discord_id,
                time_trials.c.updated_at >= text("NOW() - INTERVAL 1 DAY"),
            )
            .order_by(desc(time_trials.c.updated_at), desc(time_trials.c.id))
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

    async def get_latest_before_24h(self, user_discord_id: str) -> dict[str, int]:
        """直近24時間より前における各コースの直近の記録を取得する．

        Parameters
        ----------
        user_discord_id : str
            ユーザーのDiscord ID.

        Returns
        -------
        dict[str, int]
            コース(track)をキー, 直近の記録(time_ms)を値とする辞書．
        """
        sub_query = (
            select(
                time_trials.c.track,
                func.max(time_trials.c.updated_at).label("max_updated_at"),
            )
            .where(
                time_trials.c.user_discord_id == user_discord_id,
                time_trials.c.updated_at < text("NOW() - INTERVAL 1 DAY"),
            )
            .group_by(time_trials.c.track)
            .subquery()
        )

        query = (
            select(time_trials.c.track, time_trials.c.time_ms)
            .join(
                sub_query,
                tuple_(time_trials.c.track, time_trials.c.updated_at)
                == tuple_(sub_query.c.track, sub_query.c.max_updated_at),
            )
            .where(time_trials.c.user_discord_id == user_discord_id)
        )

        async with self.engine.connect() as conn:
            result = await conn.execute(query)

        return {data.track: data.time_ms for data in result.fetchall()}

    async def get_personal_best(
        self, user_discord_id: str, track: Track
    ) -> TimeTrialData | None:
        """指定したユーザーの指定コースの最速タイムを取得する．

        Parameters
        ----------
        user_discord_id : str
            ユーザーのDiscord ID.
        track : Track
            コース．

        Returns
        -------
        TimeTrialData | None
            最速タイム．記録がない場合はNone．
        """
        query = (
            time_trials.select()
            .where(
                time_trials.c.user_discord_id == user_discord_id,
                time_trials.c.track == track.id,
            )
            .order_by(asc(time_trials.c.time_ms))
            .limit(1)
        )

        async with self.engine.connect() as conn:
            result = await conn.execute(query)
            data = result.fetchone()

        if data is None:
            return None

        return TimeTrialData(
            id=data.id,
            user_discord_id=data.user_discord_id,
            track=data.track,
            time_ms=data.time_ms,
            created_at=data.created_at,
            updated_at=data.updated_at,
        )
