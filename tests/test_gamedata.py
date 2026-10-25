from collections import Counter

import pytest

from game_data import Game, all_tracks


@pytest.mark.parametrize("game", list(Game))
def test_track_ids_are_unique(game: Game) -> None:
    ids = [track.id for track in all_tracks(game)]
    duplicates = [id_ for id_, count in Counter(ids).items() if count > 1]
    assert not duplicates, f"IDが重複しているコース ({game.slug}): {duplicates}"
