from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

__all__ = ("Track",)


class Track(Enum):
    __slots__ = (
        "name",
        "abbr",
        "name_ja",
        "abbr_ja",
        "aliases",
    )

    def __new__(cls: type[Track], name: str, *_) -> Track:
        self = object.__new__(cls)
        self._value_ = name
        return self

    if TYPE_CHECKING:
        name: str
        abbr: str
        name_ja: str
        abbr_ja: str
        aliases: set[str]

    def __init__(
        self,
        name: str,
        abbr: str,
        name_ja: str,
        abbr_ja: str,
        aliases: set[str] | None = None,
    ) -> None:
        self.name = name
        self.abbr = abbr
        self.name_ja = name_ja
        self.abbr_ja = abbr_ja

        qual_aliases: set[str] = {
            name,
            abbr,
            name_ja,
            abbr_ja,
        }

        if aliases is not None:
            qual_aliases.update(aliases)

        # 大文字と小文字を区別せずに判別できるようにするため
        self.aliases = set(map(lambda s: s.lower(), qual_aliases))

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_nick(name: str) -> Track | None:
        for track in Track:
            if name.lower() in track.aliases:
                return track

        return None

    @staticmethod
    def search(name: str) -> list[Track]:
        ret: list[Track] = []

        for track in Track:
            if any(name.lower() in alias for alias in track.aliases):
                ret.append(track)

        return ret

    @property
    def id(self) -> str:
        return self.abbr

    @property
    def image_url(self) -> str:
        return f"https://raw.githubusercontent.com/Yumax-panda/MKWorld/refs/heads/main/tracks/{self.id}.webp"

    # TODO: 略称とエイリアスを追加する
    MBC = ("Mario Bros. Circuit", "MBC", "マリオブラザーズサーキット", "")
    CC = ("Crown City", "CC", "トロフィーシティ", "")
    WS = ("Whistlestop Summit", "WS", "シュポポコースター", "")
    DKS = ("DK Spaceport", "DKS", "DKうちゅうセンター", "")
    rDH = ("Desert Hills", "rDH", "サンサンさばく", "")
    rSGB = ("Shy Guy Bazaar", "rSGB", "ヘイホーカーニバル", "")
    rWS = ("Wario Stadium", "rWS", "ワリオスタジアム", "")
    rAF = ("Airship Fortress", "rAF", "キラーシップ", "")
    rDKP = ("DK Pass", "rDKP", "DKスノーマウンテン", "")
    SP = ("Starview Peak", "SP", "ロゼッタてんもんだい", "")
    rSHS = ("Sky-High Sundae", "rSHS", "アイスビルディング", "")
    rWSh = ("Wario Shipyard", "rWSh", "ワリオシップ", "")
    rKTB = ("Koopa Troopa Beach", "rKTB", "ノコノコビーチ", "")
    FO = ("Faraway Oasis", "FO", "リバーサイドサファリ", "")
    PS = ("Peach Stadium", "PS", "ピーチスタジアム", "")
    rPB = ("Peach Beach", "rPB", "ピーチビーチ", "")
    SSS = ("Salty Salty Speedway", "SSS", "ソルティータウン", "")
    rDDJ = ("Dino Dino Jungle", "rDDJ", "ディノディノジャングル", "")
    GBR = ("Great ? Block Ruins", "GBR", "ハテナしんでん", "")
    CCF = ("Cheep Cheep Falls", "CCF", "プクプクフォールズ", "")
    DD = ("Dandelion Depths", "DD", "ショーニューロード", "")
    BCi = ("Boo Cinema", "BCi", "おばけシネマ", "")
    DBB = ("Dry Bones Burnout", "DBB", "ホネホネツイスター", "")
    rMMM = ("Moo Moo Meadows", "rMMM", "モーモーカントリー", "")
    rCM = ("Choco Mountain", "rCM", "チョコマウンテン", "")
    rTF = ("Toad's Factory", "rTF", "キノピオファクトリー", "")
    BC = ("Bowser's Castle", "BC", "クッパキャッスル", "")
    AH = ("Acorn Heights", "AH", "どんぐりツリーハウス", "")
    rMC = ("Mario Circuit", "rMC", "マリオサーキット", "")
    RR = ("Rainbow Road", "RR", "レインボーロード", "")

    # DLC
    sMC1 = ("SNES Mario Circuit 1", "sMC1", "SFCマリオサーキット1", "")
    sMC2 = ("SNES Mario Circuit 2", "sMC2", "SFCマリオサーキット2", "")
    sMC3 = ("SNES Mario Circuit 3", "sMC3", "SFCマリオサーキット3", "")
    sGV1 = ("SNES Ghost Valley 1", "sGV1", "SFCおばけぬま1", "")
    sGV2 = ("SNES Ghost Valley 2", "sGV2", "SFCおばけぬま2", "")
    sGV3 = ("SNES Ghost Valley 3", "sGV3", "SFCおばけぬま3", "")
    sCI1 = ("SNES Choco Island 1", "sCI1", "SFCチョコレーとう1", "")
    sCI2 = ("SNES Choco Island 2", "sCI2", "SFCチョコレーとう2", "")
    sVL1 = ("SNES Vanilla Lake 1", "sVL1", "SFCバニラレイク1", "")
    sKB1 = ("SNES Koopa Beach 1", "sKB1", "SFCノコノコビーチ1", "")
