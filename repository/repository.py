from __future__ import annotations

import ssl
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

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
    __slots__ = ("_engine",)

    if TYPE_CHECKING:
        _engine: AsyncEngine

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
