from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from bot import Bot


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    bot = providers.Singleton(
        Bot, bot_token=config.bot_token, command_prefix=config.command_prefix
    )


@inject
def main(bot: Bot = Provide[Container.bot]) -> None:
    bot.run()


if __name__ == "__main__":
    container = Container()
    container.config.bot_token.from_env("BOT_TOKEN", required=True)
    container.config.command_prefix.from_env("COMMAND_PREFIX", default="!")
    container.wire(modules=[__name__])

    main()
