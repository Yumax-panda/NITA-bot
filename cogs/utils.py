from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from bot import Bot

__all__ = ("Cog",)


class Cog(commands.Cog):
    if TYPE_CHECKING:
        bot: Bot

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
