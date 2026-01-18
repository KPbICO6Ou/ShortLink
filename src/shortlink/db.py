from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from shortlink.config import get_settings

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.db_url,
            connect_args={"check_same_thread": False},
        )
    return _engine


def reset_engine() -> None:
    """Force re-creation of the engine — useful for tests that swap DB paths."""
    global _engine
    _engine = None


def init_db() -> None:
    # Importing here keeps `shortlink.db` import-cheap and avoids cycles
    # with `shortlink.models`, which itself imports from sqlmodel.
    import shortlink.models  # noqa: F401

    SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
