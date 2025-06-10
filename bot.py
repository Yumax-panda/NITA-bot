from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

__all__ = ("Bot",)


class Bot(commands.Bot):
    if TYPE_CHECKING:
        _token: str

    def __init__(self, bot_token: str, command_prefix: str) -> None:
        super().__init__(
            command_prefix=command_prefix, intents=discord.Intents.default()
        )
        self._token = bot_token

    async def on_ready(self) -> None:
        print(f"Logged on as {self.user}")

    def run(self) -> None:
        super().run(self._token)
