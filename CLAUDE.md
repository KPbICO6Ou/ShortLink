# CLAUDE.md

Project guidance for Claude Code working on `shortlink`.

## What this project is

A self-hosted URL shortener — FastAPI + SQLite + a `typer` admin CLI,
intended to run on a small VPS behind Caddy/Nginx. Designed as a hobby
project that ships as a single `pipx install`-able tool.

## Layout

- `src/shortlink/` — the package (src-layout, hatchling-built)
  - `app.py` — `create_app()` factory, FastAPI lifespan, slug
    catch-all `GET /{slug}` redirect (must stay registered **after**
    every other router, otherwise it eats their paths).
  - `api.py` — admin router at `/api/links`, gated by
    `require_admin` dependency.
  - `qr.py` — `/qr/{slug}` PNG endpoint.
  - `cli.py` — typer app, registered as `[project.scripts] shortlink`.
  - `models.py` — sqlmodel tables. `HitDaily.day` is named `day`,
    **not** `date`, because `date: date` collides with pydantic v2's
    annotation resolver.
  - `db.py` — cached engine + `init_db()` + `reset_engine()` for tests.
  - `config.py` — `Settings(BaseSettings)`, env prefix `SHORTLINK_`.
  - `schemas.py` — pydantic request/response models.
  - `slugs.py` — base62 generator.
- `tests/` — pytest + `httpx.AsyncClient` over `ASGITransport`.
- `deploy/` — systemd unit, Caddyfile, nginx.conf, backup.sh.
- `Dockerfile` / `docker-compose.yml` at repo root.

## Local commands

```bash
# install (editable, with dev extras)
pip install -e ".[dev]"

# the three CI gates — all must stay green
PYTHONPATH=src ruff check src tests
PYTHONPATH=src mypy
PYTHONPATH=src pytest -q

# spin up the API against a throwaway DB
SHORTLINK_DB_PATH=/tmp/sl.sqlite PYTHONPATH=src \
    uvicorn shortlink:app --port 8000

# the CLI, same env
SHORTLINK_DB_PATH=/tmp/sl.sqlite PYTHONPATH=src \
    python -m shortlink.cli ls
```

## Conventions

- **One milestone = one branch from `main` = one commit.** History is
  intentionally linear; squash inside the phase if you have to. Don't
  stack feature branches.
- **Backdate commits if asked** with
  `GIT_AUTHOR_DATE=... GIT_COMMITTER_DATE=... git commit ...`. The
  v0.1.0 → v1.0.0 history was assembled this way; preserve the
  ordering if you add new commits *between* tagged points.
- **`SHORTLINK_ENABLE_DOCS` defaults to off.** `/docs`, `/redoc`,
  `/openapi.json` must stay closed in prod; the Caddy and Nginx
  samples already block them too — keep those filters in sync.
- **The admin token is the only auth.** Never expose `/api/*`
  without a token check; never log it.
- **sqlmodel + mypy:** use `col(Model.field)` inside `order_by`/
  `where` when you need `.desc()` or comparison operators — bare
  `Model.field.desc()` fails mypy even though it works at runtime.
- **Ruff ignores `B008` and `E741`** — `Depends(...)` / `typer.Option(...)`
  in argument defaults is idiomatic here. Don't refactor them away.
- **Tests must not hit the network.** `health` does HEAD requests by
  design but is exercised only via direct invocation, not in
  `tests/`. If you add a health-check test, mock the httpx client.

## Things to avoid

- Don't add ORM relationships or alembic — single-file SQLite +
  `metadata.create_all()` is intentional. If we ever outgrow it, that's
  a separate migration story, not a casual refactor.
- Don't introduce a frontend framework. The README is explicit: any
  future admin UI is HTMX, no React.
- Don't expand `Settings` without env-prefixed naming
  (`SHORTLINK_*`) — operators rely on it.
- Don't `cp` the SQLite file for backups; use `sqlite3 .backup`
  (the existing `deploy/backup.sh` is the canonical path).
