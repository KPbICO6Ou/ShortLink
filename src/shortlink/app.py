from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from shortlink.api import router as admin_router
from shortlink.config import get_settings
from shortlink.db import get_session, init_db
from shortlink.models import HitDaily, Link
from shortlink.qr import router as qr_router


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
        version="0.5.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=_lifespan,
    )

    application.include_router(admin_router)
    application.include_router(qr_router)

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

        today = datetime.now(timezone.utc).date()
        daily = session.get(HitDaily, (slug, today))
        if daily is None:
            daily = HitDaily(slug=slug, day=today, count=1)
        else:
            daily.count += 1
        session.add(daily)

        session.commit()
        return RedirectResponse(url=link.target, status_code=307)

    return application


app = create_app()
