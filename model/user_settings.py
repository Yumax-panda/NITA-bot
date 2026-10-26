from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, VARCHAR, Column, Table, text

from utils.base_model import BaseModel

from .core import metadata

if TYPE_CHECKING:
    from datetime import datetime

__all__ = ("user_settings", "UserSettingData")

user_settings = Table(
    "user_settings",
    metadata,
    Column("user_discord_id", VARCHAR(25), primary_key=True),
    Column("game", VARCHAR(10), nullable=False, server_default=text("'mkworld'")),
    Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    ),
)


@dataclass(frozen=True, slots=True)
class UserSettingData(BaseModel):
    user_discord_id: str
    game: str
    updated_at: datetime
