from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, VARCHAR, Column, Integer, Table, func, text

from .core import metadata

if TYPE_CHECKING:
    from datetime import datetime

__all__ = ("time_trials", "TimeTrialData")

time_trials = Table(
    "time_trials",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # discord IDは20桁以下だが，余裕を持つ
    Column("user_discord_id", VARCHAR(25), nullable=False),
    # Track.abbrに対応, 今後のコース追加にも対応できるように長めにする．
    Column("track", VARCHAR(10), nullable=False),
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


@dataclass(frozen=True, slots=True)
class TimeTrialData:
    id: int
    user_discord_id: str
    track: str
    time_ms: int
    created_at: datetime
    updated_at: datetime
