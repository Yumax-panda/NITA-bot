from typing import TYPE_CHECKING, Any

from discord.ext import commands


class BotError(commands.CommandError):
    if TYPE_CHECKING:
        message: str | None

    def __init__(self, message: str | None = None, *args: Any) -> None:
        self.message = message
        super().__init__(message, *args)
