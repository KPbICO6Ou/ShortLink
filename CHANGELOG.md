# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

- v0.1.0 MVP scaffold on branch `feat/v0.1.0-mvp`:
  - `pyproject.toml` with `fastapi` + `uvicorn[standard]` runtime deps.
  - `src/shortlink/` package layout with `app.py` exposing the ASGI `app`.
  - `GET /{slug}` endpoint that returns `307 Temporary Redirect` to the
    stored target URL, or `404` if the slug is unknown.
  - In-memory `dict[str, str]` storage (to be replaced by SQLite in v0.2.0).
  - Hard-coded seed link `hello → https://example.com` so the redirect path
    can be exercised end-to-end.
  - Repository `.gitignore` for Python build artefacts and local databases.
