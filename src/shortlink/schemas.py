from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class LinkCreate(BaseModel):
    target: HttpUrl
    slug: str | None = Field(default=None, min_length=1, max_length=64)


class LinkRead(BaseModel):
    slug: str
    target: str
    created_at: datetime
    hits: int
