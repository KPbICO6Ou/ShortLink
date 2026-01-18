from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from shortlink.db import get_session, init_db
from shortlink.models import Link

app = FastAPI(title="shortlink", version="0.2.0")


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/{slug}")
def redirect(slug: str, session: Session = Depends(get_session)) -> RedirectResponse:
    link = session.get(Link, slug)
    if link is None:
        raise HTTPException(status_code=404, detail="slug not found")
    link.hits += 1
    session.add(link)
    session.commit()
    return RedirectResponse(url=link.target, status_code=307)
