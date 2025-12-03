# 🔗 shortlink

> **Your own self-hosted URL shortener.**
> FastAPI + SQLite + a tiny admin CLI. Runs on a $5 VPS.

Turn long URLs into short, branded ones (`https://ymi.link/x9k2`) on a domain
you control — without sending traffic data to a third-party service.

---

## ✨ Features

- ⚡ **FastAPI** redirect endpoint with `307 Temporary Redirect`
- 💾 **SQLite** storage via `sqlmodel` (typed ORM, single file)
- 🔢 **base62** auto-generated slugs, or pick your own (`--slug asr`)
- 📊 Per-link click counter and daily stats
- 🧑‍💻 Admin **CLI** (`typer`) — add / list / remove / rename from the terminal
- 🏥 `--health` flag pings every target URL and flags dead links

---

## 🚀 Quick start

```bash
# install
uv pip install -e .

# init the database
shortlink init

# add a link (auto-generated slug)
shortlink add https://github.com/yumiaura/myCat
# → http://localhost:8000/4Kx9  →  github.com/yumiaura/myCat

# or pick your own slug
shortlink add https://github.com/yumiaura/Qwen3ASRDemo --slug asr

# run the server
uvicorn shortlink:app --host 0.0.0.0 --port 8000
```

---

## 🧑‍💻 Admin CLI

```bash
shortlink ls
# slug   target                              hits   created
# asr    github.com/yumiaura/Qwen3ASRDemo      42   2026-05-22
# 4Kx9   github.com/yumiaura/myCat            118   2026-05-15

shortlink stats asr --days 7        # daily click histogram
shortlink rm 4Kx9                   # delete a link
shortlink rename asr whisper        # change a slug
shortlink health                    # check every target with HEAD requests
shortlink export links.csv          # dump everything
```

---

## 🌐 HTTP API

| Method | Path             | Description |
|--------|------------------|-------------|
| `GET`  | `/<slug>`        | Redirect to the target URL, increments hit counter |
| `GET`  | `/api/links`     | List all links (admin-token protected) |
| `POST` | `/api/links`     | Create a new link |
| `DELETE` | `/api/links/<slug>` | Remove a link |

Admin routes require `X-Admin-Token` header matching `SHORTLINK_ADMIN_TOKEN`.

---

## ⚙️ Configuration

Environment variables (or `.env`):

```bash
SHORTLINK_DB_PATH=/var/lib/shortlink/db.sqlite
SHORTLINK_BASE_URL=https://ymi.link
SHORTLINK_ADMIN_TOKEN=change-me-please
SHORTLINK_SLUG_LENGTH=4
```

---

## 🚢 Deployment

Behind Caddy on any small VPS:

```caddy
ymi.link {
    reverse_proxy localhost:8000
}
```

Then `systemctl --user enable --now shortlink.service` (unit file provided).

---

## 📦 Stack

`fastapi`, `uvicorn`, `sqlmodel`, `typer`, `httpx`, `pydantic-settings`

---

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md).

---

## 📄 License

MIT (planned).

Author: [@yumiaura](https://github.com/yumiaura)
