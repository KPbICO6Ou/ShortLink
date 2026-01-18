from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Link(SQLModel, table=True):
    slug: str = Field(primary_key=True, max_length=64)
    target: str
    created_at: datetime = Field(default_factory=_utcnow)
    hits: int = 0
