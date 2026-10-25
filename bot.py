from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING, Any

import aiohttp
import discord
from discord.ext import commands

from error import BotError

if TYPE_CHECKING:
    from discord import AppInfo, User

    from repository import Repository

__all__ = ("Bot",)

logger = logging.getLogger(__name__)

_MAX_TRACEBACK_LENGTH = 4000
extensions = [
    "cogs.meta",
    "cogs.time_trial",
]


class Bot(commands.Bot):
    if TYPE_CHECKING:
        repo: Repository
        bot_app_info: AppInfo
        owner_id: int
        session: aiohttp.ClientSession

    def __init__(
        self,
        repo: Repository,
        command_prefix: str,
        stats_webhook_url: str,
    ) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            case_insensitive=True,
            help_command=None,
        )
        self.repo = repo
        self.stats_webhook_url = stats_webhook_url

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        for extension in extensions:
            try:
                await self.load_extension(extension)
            except Exception:
                logger.exception(f"Failed to load extension {extension}.")

        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id

        await self.repo.sync()
        logger.info("Repository is ready.")

        commands = await self.tree.sync()
        logger.info(f"Successfully synced {len(commands)} commands'")

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    @property
    def owner(self) -> User:
        return self.bot_app_info.owner

    @discord.utils.cached_property
    def stats_webhook(self) -> discord.Webhook:
        return discord.Webhook.from_url(self.stats_webhook_url, session=self.session)

    async def report_error(
        self,
        exception: BaseException,
        *,
        fields: dict[str, str] | None = None,
    ) -> None:
        tb = "".join(
            traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        )
        tb = tb[-_MAX_TRACEBACK_LENGTH:]

        embed = discord.Embed(
            title=f"{type(exception).__name__} Error",
            description=f"```py\n{tb}\n```",
            colour=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )

        for name, value in (fields or {}).items():
            embed.add_field(name=name, value=value, inline=False)

        try:
            await self.stats_webhook.send(embed=embed)
        except discord.HTTPException:
            logger.exception("Failed to send error report to stats webhook.")

    async def on_ready(self) -> None:
        logger.info(f"Logged on as {self.user}")

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        logger.exception("Unhandled exception in event %s", event_method)

        _, exception, _ = sys.exc_info()

        if exception is None:
            return

        await self.report_error(
            exception,
            fields={"Event": event_method},
        )

    async def on_command_error(
        self, context: commands.Context[Bot], exception: commands.CommandError
    ) -> None:
        if isinstance(exception, BotError):
            if exception.message:
                await context.send(exception.message)
            return

        if isinstance(exception, commands.CommandNotFound):
            return

        if isinstance(exception, commands.UserInputError):
            message = "入力が正しくありません."
            command = context.command

            if command is not None:
                usage = (
                    f"{context.clean_prefix}{command.qualified_name} "
                    f"{command.usage or ''}"
                ).strip()
                message += f"\n`{usage}`"

            await context.send(message)
            return

        if isinstance(exception, commands.CommandOnCooldown):
            retry_after = f"{exception.retry_after:.1f}"
            await context.send(
                f"クールダウン中です. {retry_after}秒後に再試行してください."
            )
            return

        if isinstance(exception, commands.CheckFailure):
            await context.send("このコマンドを実行する権限がありません.")
            return

        if isinstance(exception, commands.DisabledCommand):
            await context.send("このコマンドは現在無効化されています.")
            return

        original = getattr(exception, "original", exception)

        logger.error(
            "Unhandled exception in command %s",
            context.command,
            exc_info=original,
        )

        await context.send(
            "予期しないエラーが発生しました. 時間をおいて再試行してください."
        )
        await self.report_error(
            original,
            fields={
                "Command": str(context.command),
                "User": f"{context.author} ({context.author.id})",
                "Guild": f"{context.guild} ({context.guild.id})"
                if context.guild
                else "DM",
                "Channel": f"{context.channel} ({context.channel.id})",
            },
        )
