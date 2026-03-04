from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from shortlink.api import router as admin_router
from shortlink.config import get_settings
from shortlink.db import get_session, init_db
from shortlink.models import Link


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    docs_url = "/docs" if settings.enable_docs else None
    redoc_url = "/redoc" if settings.enable_docs else None
    openapi_url = "/openapi.json" if settings.enable_docs else None

    # Initialise the DB eagerly so requests that arrive before the lifespan
    # startup completes (e.g. from ASGITransport in tests) still find the
    # schema in place. The lifespan handler keeps the production startup
    # path unchanged for `uvicorn shortlink:app`.
    init_db()

    application = FastAPI(
        title="shortlink",
        version="0.4.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=_lifespan,
    )

    application.include_router(admin_router)

    @application.get("/{slug}")
    def redirect(
        slug: str,
        session: Session = Depends(get_session),
    ) -> RedirectResponse:
        link = session.get(Link, slug)
        if link is None:
            raise HTTPException(status_code=404, detail="slug not found")
        link.hits += 1
        session.add(link)
        session.commit()
        return RedirectResponse(url=link.target, status_code=307)

    return application


app = create_app()
