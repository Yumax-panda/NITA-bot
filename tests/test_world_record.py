from cogs.helpers.world_record import WorldRecord, parse_mk8dx_leaderboard
from game_data import MK8DXTrack

SHEET = """\
,,,,,,
150cc,150cc Shroomless Time Trials Leaderboard,,,,,
,1,,header,1:00.000,,
MKS,,,,,,"Mario Kart Stadium
マリオカートスタジアム"
,All Combinations / 全てのカスタム,,,,,Meta Only / VSカスタムのみ
,1,,test_player,1:38.538*,,1
,2,,test_player2,1:38.637,,2
bCMn,,,,,,N64 Choco Mountain
,All Combinations / 全てのカスタム,,,,,
,1,, テストプレイヤー ,1:53.617,,
WP,,,,,,Water Park
,1,,test_player3,invalid,,
"""


def test_parse_mk8dx_leaderboard() -> None:
    assert parse_mk8dx_leaderboard(SHEET) == {
        MK8DXTrack.MKS.id: WorldRecord(time_ms=98538, player_name="test_player"),
        MK8DXTrack.BCMO.id: WorldRecord(time_ms=113617, player_name="テストプレイヤー"),
    }
