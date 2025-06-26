from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from repository import Repository

__all__ = ("Bot",)

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    if TYPE_CHECKING:
        _token: str
        repo: Repository

    def __init__(self, bot_token: str, repo: Repository, command_prefix: str) -> None:
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.default(),
            case_insensitive=True,
        )
        self.repo = repo
        self._token = bot_token

    async def setup_hook(self) -> None:
        await self.repo.sync()
        logger.info("Repository is ready.")

    async def on_ready(self) -> None:
        logger.info(f"Logged on as {self.user}")

    def run(self) -> None:
        super().run(self._token)
