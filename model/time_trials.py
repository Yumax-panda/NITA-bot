from sqlalchemy import TIMESTAMP, VARCHAR, Column, Integer, Table, func, text

from .core import metadata

__all__ = ("time_trials",)

time_trials = Table(
    "time_trials",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # discord IDは20桁以下だが，余裕を持つ
    Column("user_discord_id", VARCHAR(25), nullable=False),
    # 今後のコース追加にも対応できるように長めにする．
    Column("track_name", VARCHAR(50), nullable=False),
    Column("time_ms", Integer, nullable=False),
    Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
    # ref: https://docs.sqlalchemy.org/en/20/dialects/mysql.html#mysql-timestamp-onupdate
    Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    ),
)
