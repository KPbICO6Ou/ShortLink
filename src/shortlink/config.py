from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SHORTLINK_",
        env_file=".env",
        extra="ignore",
    )

    db_path: Path = Field(default=Path("shortlink.sqlite"))
    base_url: str = "http://localhost:8000"
    admin_token: str = "change-me-please"
    slug_length: int = 4

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"


def get_settings() -> Settings:
    return Settings()
