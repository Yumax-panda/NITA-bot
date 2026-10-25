from __future__ import annotations

from unittest.mock import AsyncMock

import discord
from discord.utils import MISSING

from bot import Bot

_WEBHOOK_URL = "https://discord.com/api/webhooks/123/token"


def _make_exception() -> Exception:
    try:
        raise ValueError("boom")
    except ValueError as exc:
        return exc


def _make_bot() -> Bot:
    return Bot(repo=MISSING, command_prefix="!", stats_webhook_url=_WEBHOOK_URL)


async def test_report_error_sends_embed_with_traceback() -> None:
    bot = _make_bot()
    webhook = AsyncMock(spec=discord.Webhook)
    bot.stats_webhook = webhook

    await bot.report_error(
        _make_exception(),
        fields={"Event": "on_message"},
    )

    webhook.send.assert_awaited_once()
    embed: discord.Embed = webhook.send.await_args.kwargs["embed"]
    assert embed.title == "ValueError Error"
    assert embed.colour == discord.Color.red()
    assert "ValueError" in (embed.description or "")
    assert embed.fields[0].name == "Event"
    assert embed.fields[0].value == "on_message"


async def test_report_error_swallows_http_exception() -> None:
    bot = _make_bot()
    webhook = AsyncMock(spec=discord.Webhook)
    response = AsyncMock()
    response.status = 500
    webhook.send.side_effect = discord.HTTPException(response, "failed")
    bot.stats_webhook = webhook

    await bot.report_error(_make_exception())
