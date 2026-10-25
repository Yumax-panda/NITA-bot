from __future__ import annotations

from typing import TYPE_CHECKING

from discord import app_commands

from game_data import Game, all_tracks, track_class

if TYPE_CHECKING:
    from discord import Interaction

    from bot import Bot

__all__ = ("query_track_autocomplete",)

MAX_OPTION = 25


async def query_track_autocomplete(
    interaction: Interaction[Bot], current: str
) -> list[app_commands.Choice[str]]:
    user_game = await interaction.client.repo.get_user_game(str(interaction.user.id))
    games = [user_game, *(game for game in Game if game is not user_game)]

    choices: list[app_commands.Choice[str]] = []

    for game in games:
        tracks = track_class(game).search(current) if current else all_tracks(game)

        for track in tracks:
            choices.append(
                app_commands.Choice(
                    name=f"[{game.short}] {track.ja}",
                    value=f"{game.slug}:{track.id}",
                )
            )

            if len(choices) >= MAX_OPTION:
                return choices

    return choices
