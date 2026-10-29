from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from collections.abc import Callable

    from bot import Bot
    from repository import Repository

__all__ = (
    "Cog",
    "GroupCog",
    "user_cooldown",
)

COOLDOWN_RATE = 5
COOLDOWN_PER = 10.0


def user_cooldown[T]() -> Callable[[T], T]:
    """ユーザー単位のコマンドクールダウンを付与するデコレータを返す．"""
    return commands.cooldown(COOLDOWN_RATE, COOLDOWN_PER, commands.BucketType.user)


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
