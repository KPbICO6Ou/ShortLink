# 🗺️ shortlink Roadmap

---

## v0.1.0 — MVP (1 day)

- [ ] `pyproject.toml`, `src/shortlink/`
- [ ] `GET /<slug>` returns 307 to the stored URL
- [ ] In-memory `dict[str, str]` storage (not persistent yet)
- [ ] Hard-coded seed link to prove the redirect works

Acceptance: `uvicorn shortlink:app` redirects `/hello` to `https://example.com`.

---

## v0.2.0 — SQLite persistence (1 day)

- [ ] `sqlmodel` schema: `Link(slug, target, created_at, hits)`
- [ ] `shortlink init` creates the DB at `$SHORTLINK_DB_PATH`
- [ ] `GET /<slug>` reads from DB and increments `hits`
- [ ] base62 slug generator, length configurable

---

## v0.3.0 — Admin CLI (1 day)

- [ ] `typer`-based CLI: `add`, `ls`, `rm`, `rename`
- [ ] Pretty table output via `rich`
- [ ] Reject duplicate slugs, validate URLs with `httpx`
- [ ] CSV export / import

---

## v0.4.0 — Admin HTTP API (1 day)

- [ ] `POST /api/links`, `DELETE /api/links/<slug>`, `GET /api/links`
- [ ] `X-Admin-Token` header check via FastAPI dependency
- [ ] Pydantic request/response models
- [ ] OpenAPI docs at `/docs` enabled in dev, disabled in prod

---

## v0.5.0 — Stats + health (1 day)

- [ ] Per-day hit table (`HitDaily(slug, date, count)`)
- [ ] `shortlink stats <slug> --days N` prints a histogram
- [ ] `shortlink health` runs HEAD requests against every target
- [ ] `GET /qr/<slug>` returns a PNG QR code (uses `qrcode[pil]`)

---

## v0.6.0 — Deployment polish (1 day)

- [ ] `systemd` user-service unit file
- [ ] Caddyfile and Nginx samples in `deploy/`
- [ ] Dockerfile + docker-compose for "run on any host in 30 seconds"
- [ ] Backup script: nightly `sqlite3 .backup`

---

## v1.0.0 — Release-ready

- [ ] CI: ruff + mypy + pytest (with `httpx.AsyncClient` test client)
- [ ] CHANGELOG.md following Keep a Changelog
- [ ] `pipx install shortlink`
- [ ] Screenshots / asciinema in README

---

## 🌠 Future ideas

- Per-link expiry (`--expires 2026-12-31`)
- Password-protected redirects (`/p/<slug>?key=…`)
- Web admin UI in HTMX (no React, keep it tiny)
- UTM-rewriting middleware (add `utm_source=ymi.link` automatically)
- Multi-tenant mode with per-user namespaces
