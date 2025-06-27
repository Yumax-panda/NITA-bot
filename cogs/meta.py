from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from .utils import Cog

if TYPE_CHECKING:
    from bot import Bot


# TODO
class HelpCommand(commands.HelpCommand): ...


class Meta(Cog, name="Meta", description="便利機能"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)

        self.bot.help_command = HelpCommand()
        self.bot.help_command.cog = self


async def setup(bot: Bot) -> None:
    await bot.add_cog(Meta(bot))
