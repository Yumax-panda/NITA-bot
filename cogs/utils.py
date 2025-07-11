from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from bot import Bot
    from repository import Repository

__all__ = (
    "Cog",
    "GroupCog",
)


class CogMixin:
    if TYPE_CHECKING:
        bot: Bot

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @property
    def repo(self) -> Repository:
        return self.bot.repo


class Cog(commands.Cog, CogMixin):
    pass


class GroupCog(commands.GroupCog, CogMixin):
    pass
