from __future__ import annotations

from typing import TYPE_CHECKING

from discord import app_commands

from mkworld.game_data.tracks import Track

if TYPE_CHECKING:
    from discord import Interaction

__all__ = ("query_track_autocomplete",)


async def query_track_autocomplete(
    _: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    if not current:
        return []

    return list(
        map(
            lambda t: app_commands.Choice(name=t.name_ja, value=t.name),
            Track.search(current),
        )
    )[:25]
