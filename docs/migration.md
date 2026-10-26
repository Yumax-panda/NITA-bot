# マイグレーション

[Alembic](https://alembic.sqlalchemy.org/)

## 構成

- `alembic.ini` : Alembic本体の設定。接続情報(`sqlalchemy.url`)はここでは使わず、`migrations/env.py` が `DB_*` 環境変数から構築する(`get_repository` を利用)。
- `migrations/env.py` : マイグレーション実行環境。`model/` の各テーブルを `metadata` に登録し、スキーマの比較対象とする。
  - アプリ起動時は repository 側から既存の接続(connection)が渡される。
  - CLI(`alembic` コマンド / `make` ターゲット)実行時は環境変数からエンジンを構築する。
- `migrations/versions/` : 自動生成されるリビジョンファイル。

モデル定義は `model/` 配下にある。スキーマを変更したら、該当モデルを編集してからリビジョンを生成する。

## コマンド

いずれも `DB_USERNAME` / `DB_PASSWORD` / `DB_HOSTNAME` / `DB_PORT` / `DB_NAME` / `SSL_CA_PATH` 環境変数(未設定時はローカル用デフォルト)を参照する。

| コマンド | 内容 |
| --- | --- |
| `make migrate m="reason"` | モデルとの差分から新しいリビジョンを自動生成する(`alembic revision --autogenerate`)。 |
| `make upgrade` | 未適用のマイグレーションを全て適用する(`alembic upgrade head`)。 |
| `make downgrade` | 直近のマイグレーションを1つ巻き戻す(`alembic downgrade -1`)。 |
| `make stamp` | DDLを実行せず、DBを `head` 適用済みとして記録する(`alembic stamp head`)。 |
| `make migrate-history` | リビジョン履歴と現在の適用バージョンを表示する(`alembic history` / `alembic current`)。 |

### 接続先の指定

接続先はデフォルトで `DB_*` 環境変数(未設定時はローカル用デフォルト)から構築される。環境変数を設定せずに、接続文字列を直接渡すこともできる。

- `make <target> url="mysql://user:pass@host:port/db"` のように `url` を渡す(内部で `alembic -x db_url=...` に変換される)。
- もしくは `DATABASE_URL` 環境変数に接続文字列を設定する。
- ドライバ指定(`mysql+aiomysql` など)は自動で `aiomysql` に揃うため、`mysql://` 形式でよい。
- TiDB Cloud のようにSSLが必要な場合はクエリで `?ssl_ca=/path/to/ca.pem` を付ける。

例(本番TiDBを `head` 適用済みとしてスタンプする):

```bash
make stamp url="mysql://user:pass@gateway.tidbcloud.com:4000/dbname?ssl_ca=/etc/ssl/cert.pem"
```

## 運用

### アプリ起動時の自動マイグレーション

Bot 起動時に `setup_hook` 内で `Repository.migrate()` が呼ばれ、未適用のマイグレーションが毎回自動で `head` まで適用される(`bot.py`)。マイグレーション履歴テーブル(`alembic_version`)が存在せず新規初期化された場合はログに出力される。

そのため通常運用では手動で `make upgrade` を実行する必要はない。デプロイ時に新しいリビジョンがコミットされていれば、起動時にそのまま反映される。

### Alembic管理外の既存DBへ導入する場合

既にスキーマが存在するが `alembic_version` テーブルが無いDB(Alembicを通さず作られた本番TiDBなど)は、そのまま起動すると `migrate()` が初期リビジョンの `CREATE TABLE` から流そうとして失敗する。

この場合は一度だけ `make stamp` を実行し、DDLを流さずに「`head` 適用済み」として記録する。以降は `alembic_version` が存在するため、起動時の自動マイグレーションは未適用分だけを流すようになる。

スタンプ前に、本番スキーマが現在の `head` と完全一致していることを確認すること(`alembic check`、または本番に対して `make migrate` 相当を実行して差分が空になること)。ズレがあると以降の差分適用が壊れる。

### スキーマ変更の手順

1. `model/` 配下のモデルを編集する。
2. `make migrate m="変更内容"` でリビジョンを生成する。
3. 生成された `migrations/versions/*.py` を確認し、意図通りの差分になっているか確認する。
4. ローカルで `make upgrade` を実行して適用できることを確認する。
5. リビジョンファイルをコミットする。
