from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Color, Embed
from discord.ext import commands

from .helpers.paginator import Page, Paginator
from .utils import Cog

if TYPE_CHECKING:
    from bot import Bot


class Meta(Cog, name="Meta", description="便利機能"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)

    @commands.hybrid_command(
        aliases=["h"],
        description="Botやコマンドについてのヘルプを表示する.",
    )
    async def help(self, ctx: commands.Context[Bot]) -> None:
        await ctx.defer(ephemeral=True)

        embeds: list[Embed] = []

        for cog in self.bot.cogs.values():
            commands_ = [c for c in cog.walk_commands() if not c.hidden]

            if not commands_:
                continue

            embed = Embed(
                title=cog.qualified_name,
                description=cog.description or None,
                color=Color.blue(),
            )
            embed.set_footer(text="<必須> [任意]")

            for command in sorted(commands_, key=lambda c: c.qualified_name):
                signature = command.usage or command.signature
                name = f"{ctx.clean_prefix}{command.qualified_name}"

                if signature:
                    name = f"{name} {signature}"

                description = command.description or command.short_doc or "―"
                embed.add_field(name=name, value=f"> {description}", inline=False)

            embeds.append(embed)

        pages = [Page(embed=embed) for embed in embeds]
        await Paginator(pages=pages, context=ctx).start(ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Meta(bot))
