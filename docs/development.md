# Development

## 必要なツール等

- Python
- git
- Docker
- docker-compose
- asdf
- poetry
- make

## セットアップ

asdfでPythonとNodejsをインストール & Poetryで依存関係をインストール．`make setup`

## データベース関連

-  DBコンテナをセットアップ(初回) `make setup-db`
-  DBコンテナを起動 `make up-db`
-  DBコンテナを停止 `make down-db`

## Botアカウントの取得

[ドキュメント](https://discordpy.readthedocs.io/ja/stable/discord.html#discord-intro)に従って各自作成してください．

## Botの起動

データベースを起動した状態で`make start`

## その他

- コード整形 & インポートのソート等 `make fix`
- 型チェック `make typecheck`
- テスト `make test`