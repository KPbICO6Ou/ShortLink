from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

# In-memory storage. Replaced by SQLite in v0.2.0.
links: dict[str, str] = {
    "hello": "https://example.com",
}

app = FastAPI(title="shortlink", version="0.1.0")


@app.get("/{slug}")
def redirect(slug: str) -> RedirectResponse:
    target = links.get(slug)
    if target is None:
        raise HTTPException(status_code=404, detail="slug not found")
    return RedirectResponse(url=target, status_code=307)
