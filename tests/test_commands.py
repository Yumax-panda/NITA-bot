from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import MagicMock

import pytest_asyncio
from discord import app_commands
from discord.ext import commands
from discord.utils import MISSING

from bot import Bot, extensions
from repository import Repository

type AnyCommand = (
    commands.Command[Any, ..., Any]
    | app_commands.Command[Any, ..., Any]
    | app_commands.Group
)


@pytest_asyncio.fixture
async def bot() -> AsyncIterator[Bot]:
    bot = Bot(
        repo=MagicMock(spec=Repository),
        command_prefix="!",
        stats_webhook_url=MISSING,
    )
    for extension in extensions:
        await bot.load_extension(extension)
    yield bot


async def test_all_commands_have_description(bot: Bot) -> None:
    commands_: list[AnyCommand] = [*bot.walk_commands(), *bot.tree.walk_commands()]
    missing: list[str] = [
        command.qualified_name for command in commands_ if not command.description
    ]
    assert not missing, f"descriptionが設定されていないコマンド: {missing}"


async def test_all_commands_have_cooldown(bot: Bot) -> None:
    missing: list[str] = [
        command.qualified_name
        for command in bot.walk_commands()
        if command.cooldown is None
    ]
    assert not missing, f"cooldownが設定されていないコマンド: {missing}"
