from __future__ import annotations

from .base import BaseTrack
from .game import Game

__all__ = ("Track",)


class Track(BaseTrack):
    @property
    def game(self) -> Game:
        return Game.MKWORLD

    MBC = (
        "Mario Bros. Circuit",
        "マリオブラザーズサーキット",
        "MBC",
        "",
        {"mbc", "mario bros. circuit", "マリオブラザーズサーキット"},
    )
    CC = (
        "Crown City",
        "トロフィーシティ",
        "CC",
        "",
        {"cc", "crown city", "トロフィーシティ"},
    )
    WS = (
        "Whistlestop Summit",
        "シュポポコースター",
        "WS",
        "",
        {"ws", "whistlestop summit", "シュポポコースター"},
    )
    DKS = (
        "DK Spaceport",
        "DKうちゅうセンター",
        "DKS",
        "",
        {"dks", "dk spaceport", "dkうちゅうセンター"},
    )
    rDH = (
        "Desert Hills",
        "サンサンさばく",
        "rDH",
        "",
        {"rdh", "desert hills", "サンサンさばく"},
    )
    rSGB = (
        "Shy Guy Bazaar",
        "ヘイホーカーニバル",
        "rSGB",
        "",
        {"rsgb", "shy guy bazaar", "ヘイホーカーニバル"},
    )
    rWS = (
        "Wario Stadium",
        "ワリオスタジアム",
        "rWS",
        "",
        {"rws", "wario stadium", "ワリオスタジアム"},
    )
    rAF = (
        "Airship Fortress",
        "キラーシップ",
        "rAF",
        "",
        {"raf", "airship fortress", "キラーシップ"},
    )
    rDKP = (
        "DK Pass",
        "DKスノーマウンテン",
        "rDKP",
        "",
        {"rdkp", "dk pass", "dkスノーマウンテン"},
    )
    SP = (
        "Starview Peak",
        "ロゼッタてんもんだい",
        "SP",
        "",
        {"sp", "starview peak", "ロゼッタてんもんだい"},
    )
    rSHS = (
        "Sky-High Sundae",
        "アイスビルディング",
        "rSHS",
        "",
        {"rshs", "sky-high sundae", "アイスビルディング"},
    )
    rWSh = (
        "Wario Shipyard",
        "ワリオシップ",
        "rWSh",
        "",
        {"rwsh", "wario shipyard", "ワリオシップ"},
    )
    rKTB = (
        "Koopa Troopa Beach",
        "ノコノコビーチ",
        "rKTB",
        "",
        {"rktb", "koopa troopa beach", "ノコノコビーチ"},
    )
    FO = (
        "Faraway Oasis",
        "リバーサイドサファリ",
        "FO",
        "",
        {"fo", "faraway oasis", "リバーサイドサファリ"},
    )
    PS = (
        "Peach Stadium",
        "ピーチスタジアム",
        "PS",
        "",
        {"ps", "peach stadium", "ピーチスタジアム"},
    )
    rPB = (
        "Peach Beach",
        "ピーチビーチ",
        "rPB",
        "",
        {"rpb", "peach beach", "ピーチビーチ"},
    )
    SSS = (
        "Salty Salty Speedway",
        "ソルティータウン",
        "SSS",
        "",
        {"sss", "salty salty speedway", "ソルティータウン"},
    )
    rDDJ = (
        "Dino Dino Jungle",
        "ディノディノジャングル",
        "rDDJ",
        "",
        {"rddj", "dino dino jungle", "ディノディノジャングル"},
    )
    GBR = (
        "Great ? Block Ruins",
        "ハテナしんでん",
        "GBR",
        "",
        {"gbr", "great ? block ruins", "ハテナしんでん"},
    )
    CCF = (
        "Cheep Cheep Falls",
        "プクプクフォールズ",
        "CCF",
        "",
        {"ccf", "cheep cheep falls", "プクプクフォールズ"},
    )
    DD = (
        "Dandelion Depths",
        "ショーニューロード",
        "DD",
        "",
        {"dd", "dandelion depths", "ショーニューロード"},
    )
    BCi = (
        "Boo Cinema",
        "おばけシネマ",
        "BCi",
        "",
        {"bci", "boo cinema", "おばけシネマ"},
    )
    DBB = (
        "Dry Bones Burnout",
        "ホネホネツイスター",
        "DBB",
        "",
        {"dbb", "dry bones burnout", "ホネホネツイスター"},
    )
    rMMM = (
        "Moo Moo Meadows",
        "モーモーカントリー",
        "rMMM",
        "",
        {"rmmm", "moo moo meadows", "モーモーカントリー"},
    )
    rCM = (
        "Choco Mountain",
        "チョコマウンテン",
        "rCM",
        "",
        {"rcm", "choco mountain", "チョコマウンテン"},
    )
    rTF = (
        "Toad's Factory",
        "キノピオファクトリー",
        "rTF",
        "",
        {"rtf", "toad's factory", "キノピオファクトリー"},
    )
    BC = (
        "Bowser's Castle",
        "クッパキャッスル",
        "BC",
        "",
        {"bc", "bowser's castle", "クッパキャッスル"},
    )
    AH = (
        "Acorn Heights",
        "どんぐりツリーハウス",
        "AH",
        "",
        {"ah", "acorn heights", "どんぐりツリーハウス"},
    )
    rMC = (
        "Mario Circuit",
        "マリオサーキット",
        "rMC",
        "",
        {"rmc", "mario circuit", "マリオサーキット"},
    )
    RR = (
        "Rainbow Road",
        "レインボーロード",
        "RR",
        "",
        {"rr", "rainbow road", "レインボーロード"},
    )
    sMC1 = (
        "SNES Mario Circuit 1",
        "SFCマリオサーキット1",
        "sMC1",
        "",
        {"smc1", "snes mario circuit 1", "sfcマリオサーキット1"},
    )
    sMC2 = (
        "SNES Mario Circuit 2",
        "SFCマリオサーキット2",
        "sMC2",
        "",
        {"smc2", "snes mario circuit 2", "sfcマリオサーキット2"},
    )
    sMC3 = (
        "SNES Mario Circuit 3",
        "SFCマリオサーキット3",
        "sMC3",
        "",
        {"smc3", "snes mario circuit 3", "sfcマリオサーキット3"},
    )
    sGV1 = (
        "SNES Ghost Valley 1",
        "SFCおばけぬま1",
        "sGV1",
        "",
        {"sgv1", "snes ghost valley 1", "sfcおばけぬま1"},
    )
    sGV2 = (
        "SNES Ghost Valley 2",
        "SFCおばけぬま2",
        "sGV2",
        "",
        {"sgv2", "snes ghost valley 2", "sfcおばけぬま2"},
    )
    sGV3 = (
        "SNES Ghost Valley 3",
        "SFCおばけぬま3",
        "sGV3",
        "",
        {"sgv3", "snes ghost valley 3", "sfcおばけぬま3"},
    )
    sCI1 = (
        "SNES Choco Island 1",
        "SFCチョコレーとう1",
        "sCI1",
        "",
        {"sci1", "snes choco island 1", "sfcチョコレーとう1"},
    )
    sCI2 = (
        "SNES Choco Island 2",
        "SFCチョコレーとう2",
        "sCI2",
        "",
        {"sci2", "snes choco island 2", "sfcチョコレーとう2"},
    )
    sVL1 = (
        "SNES Vanilla Lake 1",
        "SFCバニラレイク1",
        "sVL1",
        "",
        {"svl1", "snes vanilla lake 1", "sfcバニラレイク1"},
    )
    sKB1 = (
        "SNES Koopa Beach 1",
        "SFCノコノコビーチ1",
        "sKB1",
        "",
        {"skb1", "snes koopa beach 1", "sfcノコノコビーチ1"},
    )
