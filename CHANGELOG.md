# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

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
