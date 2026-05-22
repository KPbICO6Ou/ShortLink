import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlmodel import Session, col, select

from shortlink.config import Settings, get_settings
from shortlink.db import get_session
from shortlink.models import Link
from shortlink.schemas import LinkCreate, LinkRead
from shortlink.slugs import generate_slug

router = APIRouter(prefix="/api/links", tags=["admin"])


def require_admin(
    x_admin_token: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    # Refuse to authenticate at all when no token is configured — otherwise an
    # operator who forgot to set SHORTLINK_ADMIN_TOKEN would expose admin
    # endpoints to anyone who can send an empty X-Admin-Token header.
    if not settings.admin_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin API disabled: SHORTLINK_ADMIN_TOKEN is not configured",
        )
    if not x_admin_token or not secrets.compare_digest(
        x_admin_token, settings.admin_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing admin token",
        )


@router.get("", response_model=list[LinkRead], dependencies=[Depends(require_admin)])
def list_links(session: Session = Depends(get_session)) -> list[Link]:
    return list(session.exec(select(Link).order_by(col(Link.created_at).desc())).all())


@router.post(
    "",
    response_model=LinkRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_link(
    payload: LinkCreate,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> Link:
    slug = payload.slug
    if slug is None:
        for _ in range(10):
            candidate = generate_slug(settings.slug_length)
            if session.get(Link, candidate) is None:
                slug = candidate
                break
        else:
            raise HTTPException(status_code=500, detail="could not allocate a slug")
    elif session.get(Link, slug) is not None:
        raise HTTPException(status_code=409, detail="slug already exists")

    link = Link(slug=slug, target=str(payload.target))
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_link(slug: str, session: Session = Depends(get_session)) -> None:
    link = session.get(Link, slug)
    if link is None:
        raise HTTPException(status_code=404, detail="slug not found")
    session.delete(link)
    session.commit()
