# shortLink

A self-hosted URL shortener built around FastAPI, SQLite and a small `typer`
admin CLI. It is designed to run on a single small VPS behind Caddy or Nginx
and to be installable as a single binary via `pipx`.

[![CI](https://github.com/KPbICO6Ou/ShortLink/actions/workflows/ci.yml/badge.svg)](https://github.com/KPbICO6Ou/ShortLink/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](#license)

## Features

- `GET /{slug}` redirects to the stored URL with `307 Temporary Redirect`
- SQLite storage via `sqlmodel`; no external database required
- Base62 slug generator, with optional custom slugs
- Per-link hit counter plus a per-day hit table for histograms
- Admin HTTP API at `/api/links`, gated by an `X-Admin-Token` header
- `GET /qr/{slug}` returns a PNG QR code for the short URL
- `shortlink` CLI: `add`, `ls`, `rm`, `rename`, `stats`, `health`,
  `export`, `import`, `init`
- Production deployment artefacts: `systemd` unit, Caddy and Nginx samples,
  Dockerfile, `docker-compose.yml`, nightly backup script

## Requirements

- Python 3.11 or newer
- SQLite (bundled with Python)

## Installation

From source, into an isolated environment:

```bash
git clone https://github.com/KPbICO6Ou/ShortLink.git
cd ShortLink
pipx install .
```

For development work, install in editable mode with the dev extras:

```bash
pip install -e ".[dev]"
```

## Quick start

```bash
# Initialise the database at $SHORTLINK_DB_PATH (defaults to ./shortlink.sqlite)
shortlink init

# Add a link with an auto-generated base62 slug
shortlink add https://example.com/some/long/path
# → http://localhost:8000/4Kx9  →  https://example.com/some/long/path

# Or pick the slug yourself
shortlink add https://example.com/blog --slug blog

# Serve the redirect endpoint
uvicorn shortlink:app --host 0.0.0.0 --port 8000
```

## CLI reference

| Command                         | Description                                        |
| ------------------------------- | -------------------------------------------------- |
| `shortlink init`                | Create the database file and schema                |
| `shortlink add <url> [--slug]`  | Add a link; generates a slug if `--slug` is absent |
| `shortlink ls`                  | List every link as a rich table                    |
| `shortlink rm <slug>`           | Delete a link                                      |
| `shortlink rename <old> <new>`  | Move a link to a new slug                          |
| `shortlink stats <slug> -d N`   | Per-day click histogram over the last N days       |
| `shortlink health`              | HEAD-check every target URL; exit non-zero on dead |
| `shortlink export <path>`       | Dump every link to CSV                             |
| `shortlink import <path>`       | Bulk-add from a CSV produced by `export`           |

## HTTP API

| Method   | Path                  | Auth        | Description                       |
| -------- | --------------------- | ----------- | --------------------------------- |
| `GET`    | `/{slug}`             | public      | Redirect to target; increment hits |
| `GET`    | `/qr/{slug}`          | public      | PNG QR code for the short URL     |
| `GET`    | `/api/links`          | admin token | List all links                    |
| `POST`   | `/api/links`          | admin token | Create a link                     |
| `DELETE` | `/api/links/{slug}`   | admin token | Delete a link                     |

Admin endpoints require an `X-Admin-Token` header that matches
`SHORTLINK_ADMIN_TOKEN`. Requests without it return `401`.

The OpenAPI schema and Swagger UI are disabled by default. Set
`SHORTLINK_ENABLE_DOCS=1` to expose `/docs`, `/redoc` and `/openapi.json` —
the Caddy and Nginx samples in `deploy/` block those paths regardless, so
production exposure is opt-in on both layers.

## Configuration

All settings are read from environment variables with the `SHORTLINK_`
prefix (or a `.env` file in the working directory):

| Variable                  | Default                | Purpose                                    |
| ------------------------- | ---------------------- | ------------------------------------------ |
| `SHORTLINK_DB_PATH`       | `shortlink.sqlite`     | SQLite database file path                  |
| `SHORTLINK_BASE_URL`      | `http://localhost:8000`| Used by the CLI when printing short URLs   |
| `SHORTLINK_ADMIN_TOKEN`   | _(unset)_              | Required value of the `X-Admin-Token` header. The admin API returns `503` until this is set. Use `deploy/setup.py` to mint one. |
| `SHORTLINK_SLUG_LENGTH`   | `4`                    | Length of auto-generated base62 slugs      |
| `SHORTLINK_ENABLE_DOCS`   | `false`                | Expose `/docs`, `/redoc`, `/openapi.json`  |

## Deployment

Ready-to-use samples live in `deploy/`:

- `deploy/shortlink.service` — `systemd` user unit
- `deploy/Caddyfile` — TLS-terminating reverse proxy
- `deploy/nginx.conf` — alternative reverse proxy
- `deploy/backup.sh` — nightly snapshot using `sqlite3 .backup`

A minimal Caddy setup:

```caddy
links.example.com {
    reverse_proxy localhost:8000
}
```

A container image is provided as well:

```bash
docker compose up -d
```

## Development

The repository ships three CI gates; all three must stay green:

```bash
PYTHONPATH=src ruff check src tests
PYTHONPATH=src mypy
PYTHONPATH=src pytest -q
```

Tests run against a throwaway SQLite database and never touch the network.

## License

MIT.

See [CHANGELOG.md](CHANGELOG.md) for release history.
