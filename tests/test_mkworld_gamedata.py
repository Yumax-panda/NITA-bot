from collections import Counter

from mkworld.game_data.tracks import Track


def test_track_ids_are_unique() -> None:
    ids = [track.id for track in Track]
    duplicates = [id_ for id_, count in Counter(ids).items() if count > 1]
    assert not duplicates, f"IDが重複しているコース: {duplicates}"
