import io

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlmodel import Session

from shortlink.config import Settings, get_settings
from shortlink.db import get_session
from shortlink.models import Link

router = APIRouter(prefix="/qr", tags=["qr"])


@router.get("/{slug}")
def qr_png(
    slug: str,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> Response:
    link = session.get(Link, slug)
    if link is None:
        raise HTTPException(status_code=404, detail="slug not found")
    short_url = f"{settings.base_url.rstrip('/')}/{slug}"
    img = qrcode.make(short_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
