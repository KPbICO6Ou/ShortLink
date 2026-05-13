from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import httpx
import pytest


@pytest.fixture
def settings_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Isolate every test in its own SQLite file and clear cached engines."""
    db = tmp_path / "test.sqlite"
    monkeypatch.setenv("SHORTLINK_DB_PATH", str(db))
    monkeypatch.setenv("SHORTLINK_ADMIN_TOKEN", "test-token")
    monkeypatch.setenv("SHORTLINK_BASE_URL", "http://test")
    monkeypatch.setenv("SHORTLINK_SLUG_LENGTH", "4")
    monkeypatch.setenv("SHORTLINK_ENABLE_DOCS", "true")

    from shortlink.config import get_settings
    from shortlink.db import reset_engine

    get_settings.cache_clear() if hasattr(get_settings, "cache_clear") else None
    reset_engine()
    yield db
    reset_engine()


@pytest.fixture
async def client(settings_env: Path) -> AsyncIterator[httpx.AsyncClient]:
    from shortlink.app import create_app

    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
