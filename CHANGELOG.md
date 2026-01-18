# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

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
