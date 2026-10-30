import asyncio
import os
import ssl
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection, make_url
from sqlalchemy.ext.asyncio import create_async_engine

# これらのimportはTableをmetadataに登録するために必要．
import model.time_trials  # noqa: F401
import model.user_settings  # noqa: F401
from model.core import metadata
from repository import get_repository

config = context.config

# アプリ起動時(connectionが渡される)はアプリ側でロギング設定済みなので
# fileConfigを呼ばない．呼ぶと既存ロガーが無効化され, 二重出力やログ消失を招く．
if config.config_file_name is not None and config.attributes.get("connection") is None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def _build_engine():
    url = context.get_x_argument(as_dictionary=True).get("db_url") or os.environ.get(
        "DATABASE_URL"
    )
    if url:
        url = make_url(url).set(drivername="mysql+aiomysql")
        query = dict(url.query)
        ssl_ca = query.pop("ssl_ca", None)
        url = url.set(query=query)

        ssl_ca_path = (ssl_ca[0] if isinstance(ssl_ca, tuple) else ssl_ca) or (
            os.environ.get("SSL_CA_PATH")
        )

        if ssl_ca_path:
            ssl_context = ssl.create_default_context(cafile=ssl_ca_path)
            return create_async_engine(
                url, pool_pre_ping=True, connect_args={"ssl": ssl_context}
            )
        return create_async_engine(url, pool_pre_ping=True)

    return get_repository(
        user=os.environ.get("DB_USERNAME", "root"),
        password=os.environ.get("DB_PASSWORD", "password"),
        host_name=os.environ.get("DB_HOSTNAME", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        db_name=os.environ.get("DB_NAME", "mkbot"),
        ssl_ca_path=os.environ.get("SSL_CA_PATH") or None,
    ).engine


def run_migrations_offline() -> None:
    engine = _build_engine()
    context.configure(
        url=engine.url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = _build_engine()

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    connection = config.attributes.get("connection", None)
    if connection is not None:
        do_run_migrations(connection)
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
