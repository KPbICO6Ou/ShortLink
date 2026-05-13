from datetime import UTC, datetime
from datetime import date as Date

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _today() -> Date:
    return datetime.now(UTC).date()


class Link(SQLModel, table=True):
    slug: str = Field(primary_key=True, max_length=64)
    target: str
    created_at: datetime = Field(default_factory=_utcnow)
    hits: int = 0


class HitDaily(SQLModel, table=True):
    __tablename__ = "hit_daily"

    slug: str = Field(primary_key=True, max_length=64, index=True)
    day: Date = Field(primary_key=True, default_factory=_today)
    count: int = 0
