from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord.ext import commands

from error import BotError

if TYPE_CHECKING:
    from discord import AppInfo, User

    from repository import Repository

__all__ = ("Bot",)

logger = logging.getLogger(__name__)
extensions = [
    "cogs.meta",
    "cogs.time_trial",
]


class Bot(commands.Bot):
    if TYPE_CHECKING:
        _token: str
        repo: Repository
        bot_app_info: AppInfo
        owner_id: int
        session: aiohttp.ClientSession

    def __init__(self, bot_token: str, repo: Repository, command_prefix: str) -> None:
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
        self._token = bot_token

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

    async def on_ready(self) -> None:
        logger.info(f"Logged on as {self.user}")

    def run(self) -> None:
        super().run(self._token)

    # TODO
    async def on_command_error(
        self, context: commands.Context[Bot], exception: commands.CommandError
    ) -> None:
        if isinstance(exception, BotError):
            await context.send(exception.message)
