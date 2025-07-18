from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord.ext import commands

from .utils import Cog

if TYPE_CHECKING:
    from bot import Bot


# TODO
class HelpCommand(commands.HelpCommand):
    if TYPE_CHECKING:
        context: commands.Context[Bot]

    def __init__(self) -> None:
        super().__init__(
            command_attrs={
                "cooldown": commands.CooldownMapping.from_cooldown(
                    1, 3.0, commands.BucketType.member
                ),
                "help": "Botやコマンドについてのヘルプを表示",
            }
        )

    async def send_bot_help(self, _: Any) -> None: ...


class Meta(Cog, name="Meta", description="便利機能"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)

        self.bot.help_command = HelpCommand()
        self.bot.help_command.cog = self


async def setup(bot: Bot) -> None:
    await bot.add_cog(Meta(bot))
