from datetime import UTC, datetime
from datetime import date as Date

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


def today_utc() -> Date:
    return datetime.now(UTC).date()


class Link(SQLModel, table=True):
    slug: str = Field(primary_key=True, max_length=64)
    target: str
    created_at: datetime = Field(default_factory=utcnow)
    hits: int = 0


class HitDaily(SQLModel, table=True):
    __tablename__ = "hit_daily"

    slug: str = Field(primary_key=True, max_length=64, index=True)
    day: Date = Field(primary_key=True, default_factory=today_utc)
    count: int = 0
