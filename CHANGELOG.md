# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

_Nothing yet._

## 1.0.0 — 2026-05-13

First stable release. Squashes the v0.1.0 → v0.6.0 milestones into a
single shippable artefact and adds release-readiness work on branch
`release/v1.0.0`.

### Added

- v1.0.0 Release readiness on branch `release/v1.0.0`:
  - `tests/` suite using `pytest` + `pytest-asyncio` + `httpx.AsyncClient`
    against an `ASGITransport`-backed app; covers redirect / hit
    counting, 404 on missing slug, admin-token gating, create/delete,
    auto-slug, and the QR PNG endpoint.
  - `tests/conftest.py` exposes a `client` fixture that builds a fresh
    `create_app()` per test with an isolated SQLite file under tmp_path.
  - `pyproject.toml` gains `ruff`, `mypy`, `pytest-asyncio` dev extras
    and `[tool.ruff]`/`[tool.mypy]`/`[tool.pytest.ini_options]` blocks.
    `B008` and `E741` are ignored because `Depends(...)` in defaults is
    idiomatic in FastAPI/typer code.
  - `mypy` clean across the package — required swapping
    `Model.col.desc()` for `col(Model.col).desc()` so the SQL construct
    is visible to the type checker.
  - `.github/workflows/ci.yml` runs ruff, mypy, and pytest on a 3.11 /
    3.12 matrix on every push to main and every PR.
  - `pipx install shortlink` is now wired through `[project.scripts]`
    (the entrypoint was added in v0.2.0; this release confirms it).

- v0.6.0 Deployment polish on branch `feat/v0.6.0-deploy`:
  - `deploy/shortlink.service` — systemd user-unit running
    `uvicorn shortlink:app` against `~/shortlink/.env`, with
    `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=strict` and a
    narrow `ReadWritePaths`.
  - `deploy/Caddyfile` — production-style reverse-proxy with
    automatic TLS and a `respond 404` block over `/api`, `/docs`,
    `/redoc`, `/openapi.json` so the admin surface never leaks to
    the public web.
  - `deploy/nginx.conf` — equivalent nginx server block (HTTP→HTTPS
    redirect, commented certbot lines, same admin-path block).
  - `Dockerfile` — slim python:3.12 image, cached pip layer, default
    SQLite path at `/data/shortlink.sqlite`, exposes 8000.
  - `docker-compose.yml` — single-service stack bound to
    `127.0.0.1:8000` (intended to live behind Caddy/Nginx),
    persistent named volume `shortlink-data`, env file template.
  - `deploy/backup.sh` — nightly `sqlite3 .backup` snapshot with
    timestamped filenames, gzip compression, and a retention prune.

- v0.5.0 Stats, health and QR codes on branch `feat/v0.5.0-stats-health`:
  - New `HitDaily(slug, day, count)` table; every successful redirect
    upserts the (slug, today) row in the same transaction that bumps
    `Link.hits`. Field is named `day`, not `date`, to avoid a name clash
    with the `datetime.date` annotation that breaks pydantic v2.
  - `shortlink stats <slug> --days N` prints a per-day text histogram
    scaled to the largest bucket; fails non-zero if the slug is unknown.
  - `shortlink health [--timeout S]` issues HEAD requests against every
    target via `httpx` (following redirects), renders a rich table
    with colour-coded statuses, and exits non-zero if anything is dead.
  - `GET /qr/<slug>` returns a PNG QR code that encodes
    `SHORTLINK_BASE_URL/<slug>`, sourced from `qrcode[pil]`.

- v0.4.0 Admin HTTP API on branch `feat/v0.4.0-admin-api`:
  - `POST /api/links`, `GET /api/links`, `DELETE /api/links/{slug}`
    under an `admin` OpenAPI tag, all gated by an `X-Admin-Token`
    FastAPI dependency that compares against `SHORTLINK_ADMIN_TOKEN`.
  - Pydantic request/response models (`LinkCreate`, `LinkRead`) with
    `HttpUrl` validation — invalid targets return 422.
  - `SHORTLINK_ENABLE_DOCS` flag controls `/docs`, `/redoc`, and
    `/openapi.json`; defaults to off so production deployments don't
    leak the admin schema.
  - App construction moved to a `create_app()` factory and a FastAPI
    lifespan handler so the same module supports both `uvicorn
    shortlink:app` and per-test app instances.

- v0.3.0 Admin CLI on branch `feat/v0.3.0-admin-cli`:
  - Full `typer` command set: `add`, `ls`, `rm`, `rename`, `export`,
    `import`, in addition to the existing `init`.
  - `ls` renders a `rich` table sorted by `created_at` descending,
    showing slug, target, hits, and created date.
  - `add` auto-generates a base62 slug of `SHORTLINK_SLUG_LENGTH` and
    retries up to 10 times if it collides; otherwise honours `--slug`.
  - Duplicate-slug rejection on both `add` and `rename`.
  - URL validation via `httpx.URL`: scheme must be http/https and the
    URL must have a host. Invalid input fails with a typer BadParameter
    so the exit code is 2.
  - `export` writes every link to a four-column CSV
    (`slug,target,created_at,hits`); `import` reads such a CSV and
    skips slugs that already exist.

- v0.2.0 SQLite persistence on branch `feat/v0.2.0-sqlite`:
  - `Link(slug, target, created_at, hits)` model via `sqlmodel`.
  - `shortlink.config.Settings` (pydantic-settings) reads
    `SHORTLINK_DB_PATH`, `SHORTLINK_BASE_URL`, `SHORTLINK_ADMIN_TOKEN`,
    `SHORTLINK_SLUG_LENGTH` from env / `.env`.
  - `shortlink.db` exposes a cached engine and `init_db()` that creates
    the schema.
  - `shortlink init` CLI (typer) creates the DB at `$SHORTLINK_DB_PATH`.
  - `GET /{slug}` now reads from the DB and atomically increments
    `hits` on every successful redirect.
  - `shortlink.slugs.generate_slug(length)` returns a configurable-length
    base62 slug backed by `secrets.choice`.

- v0.1.0 MVP scaffold on branch `feat/v0.1.0-mvp`:
  - `pyproject.toml` with `fastapi` + `uvicorn[standard]` runtime deps.
  - `src/shortlink/` package layout with `app.py` exposing the ASGI `app`.
  - `GET /{slug}` endpoint that returns `307 Temporary Redirect` to the
    stored target URL, or `404` if the slug is unknown.
  - In-memory `dict[str, str]` storage (to be replaced by SQLite in v0.2.0).
  - Hard-coded seed link `hello → https://example.com` so the redirect path
    can be exercised end-to-end.
  - Repository `.gitignore` for Python build artefacts and local databases.
