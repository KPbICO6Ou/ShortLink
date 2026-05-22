from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


SLUG_PATTERN = r"^[A-Za-z0-9_-]+$"


class LinkCreate(BaseModel):
    target: HttpUrl
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        pattern=SLUG_PATTERN,
    )


class LinkRead(BaseModel):
    slug: str
    target: str
    created_at: datetime
    hits: int
