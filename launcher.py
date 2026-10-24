import logging
import os

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from discord.utils import setup_logging

from bot import Bot
from repository import get_repository

ENV = os.environ.get("ENV", "production")
IS_DEV = ENV == "dev"

setup_logging(level=logging.DEBUG if IS_DEV else logging.INFO)
logging.getLogger("discord").setLevel(logging.WARNING)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    repo = providers.Singleton(
        get_repository,
        user=config.db_user,
        password=config.db_password,
        host_name=config.db_hostname,
        port=config.db_port,
        db_name=config.db_name,
        ssl_ca_path=config.ssl_ca_path,
        echo=config.sql_echo,
    )

    bot = providers.Singleton(
        Bot,
        repo=repo,
        command_prefix=config.command_prefix,
    )


@inject
def main(
    bot: Bot = Provide[Container.bot],
    token: str = Provide[Container.config.bot_token],
) -> None:
    bot.run(token)


if __name__ == "__main__":
    container = Container()
    container.config.db_user.from_env("DB_USERNAME", default="root")
    container.config.db_password.from_env("DB_PASSWORD", default="password")
    container.config.db_hostname.from_env("DB_HOSTNAME", default="localhost")
    container.config.db_port.from_env("DB_PORT", as_=int, default=3306)
    container.config.db_name.from_env("DB_NAME", default="mkbot")
    container.config.ssl_ca_path.from_env("SSL_CA_PATH", default=None)
    container.config.sql_echo.from_value(IS_DEV)
    container.config.bot_token.from_env("BOT_TOKEN")
    container.config.command_prefix.from_env("COMMAND_PREFIX", default="!")
    container.config.from_yaml("./config.local.yml")
    container.config.load()
    container.wire(modules=[__name__])

    main()
