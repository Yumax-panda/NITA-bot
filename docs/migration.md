# マイグレーション

[Alembic](https://alembic.sqlalchemy.org/)

## コマンド

| コマンド | 内容 |
| --- | --- |
| `make migrate m="reason"` | モデルとの差分から新しいリビジョンを自動生成する(`alembic revision --autogenerate`)。 |
| `make upgrade` | 未適用のマイグレーションを全て適用する(`alembic upgrade head`)。 |
| `make downgrade` | 直近のマイグレーションを1つ巻き戻す(`alembic downgrade -1`)。 |
| `make stamp` | DDLを実行せず、DBを `head` 適用済みとして記録する(`alembic stamp head`)。 |
| `make migrate-history` | リビジョン履歴と現在の適用バージョンを表示する(`alembic history` / `alembic current`)。 |

例

```bash
make stamp url="mysql://user:pass@gateway.tidbcloud.com:4000/dbname?ssl_ca=/etc/ssl/cert.pem"
```

## Alembic管理外の既存DBへ導入する場合

`make stamp`を実行する．

## スキーマ変更の手順

1. `model/` 配下のモデルを編集する。
2. `make migrate m="変更内容"` でリビジョンを生成する。
3. 生成された `migrations/versions/*.py` を確認し、意図通りの差分になっているか確認する。
4. ローカルで `make upgrade` を実行して適用できることを確認する。
5. リビジョンファイルをコミットする。
