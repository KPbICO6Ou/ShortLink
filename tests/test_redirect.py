import httpx
import pytest

HEADERS = {"X-Admin-Token": "test-token"}


async def test_redirect_increments_hits(client: httpx.AsyncClient) -> None:
    r = await client.post(
        "/api/links",
        json={"target": "https://example.com/", "slug": "hi"},
        headers=HEADERS,
    )
    assert r.status_code == 201

    r = await client.get("/hi")
    assert r.status_code == 307
    assert r.headers["location"] == "https://example.com/"

    await client.get("/hi")
    listing = (await client.get("/api/links", headers=HEADERS)).json()
    assert next(l for l in listing if l["slug"] == "hi")["hits"] == 2


async def test_missing_slug_returns_404(client: httpx.AsyncClient) -> None:
    r = await client.get("/does-not-exist")
    assert r.status_code == 404


@pytest.mark.parametrize("target", ["not-a-url", "javascript:alert(1)"])
async def test_invalid_target_rejected(client: httpx.AsyncClient, target: str) -> None:
    r = await client.post(
        "/api/links",
        json={"target": target, "slug": "x"},
        headers=HEADERS,
    )
    assert r.status_code == 422
