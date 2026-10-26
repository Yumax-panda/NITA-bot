from __future__ import annotations

from typing import TYPE_CHECKING

from discord import app_commands

from game_data import all_tracks, track_class

if TYPE_CHECKING:
    from discord import Interaction

    from bot import Bot

__all__ = ("track_autocomplete",)

MAX_OPTION = 25


async def track_autocomplete(
    interaction: Interaction[Bot], current: str
) -> list[app_commands.Choice[str]]:
    game = await interaction.client.repo.get_user_game(str(interaction.user.id))
    cls = track_class(game)
    tracks = cls.search(current) if current else all_tracks(game)

    return [
        app_commands.Choice(name=track.ja, value=track.id)
        for track in tracks[:MAX_OPTION]
    ]
