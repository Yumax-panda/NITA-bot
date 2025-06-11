from __future__ import annotations

import ssl
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

__all__ = ("Config", "Repository")


class Config:
    __slots__ = ("user", "password", "host_name", "port", "db_name", "ssl_ca_path")

    if TYPE_CHECKING:
        user: str
        password: str
        host_name: str
        port: int
        db_name: str
        ssl_ca_path: str | None

    def __init__(
        self,
        user: str,
        password: str,
        host_name: str,
        port: int,
        db_name: str,
        ssl_ca_path: str | None = None,
    ) -> None:
        self.user = user
        self.password = password
        self.host_name = host_name
        self.port = port
        self.db_name = db_name
        self.ssl_ca_path = ssl_ca_path

    def get_repository(self) -> Repository:
        dsn = f"mysql+aiomysql://{self.user}:{self.password}@{self.host_name}:{self.port}/{self.db_name}"

        if self.ssl_ca_path:
            ssl_context = ssl.create_default_context(cafile=self.ssl_ca_path)
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
