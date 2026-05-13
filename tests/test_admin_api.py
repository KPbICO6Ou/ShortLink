import httpx

HEADERS = {"X-Admin-Token": "test-token"}


async def test_admin_requires_token(client: httpx.AsyncClient) -> None:
    assert (await client.get("/api/links")).status_code == 401
    assert (await client.get("/api/links", headers={"X-Admin-Token": "wrong"})).status_code == 401


async def test_create_and_delete(client: httpx.AsyncClient) -> None:
    r = await client.post(
        "/api/links",
        json={"target": "https://example.com/", "slug": "foo"},
        headers=HEADERS,
    )
    assert r.status_code == 201

    r = await client.post(
        "/api/links",
        json={"target": "https://example.com/", "slug": "foo"},
        headers=HEADERS,
    )
    assert r.status_code == 409

    r = await client.delete("/api/links/foo", headers=HEADERS)
    assert r.status_code == 204
    r = await client.delete("/api/links/foo", headers=HEADERS)
    assert r.status_code == 404


async def test_auto_slug(client: httpx.AsyncClient) -> None:
    r = await client.post(
        "/api/links",
        json={"target": "https://example.com/"},
        headers=HEADERS,
    )
    assert r.status_code == 201
    assert len(r.json()["slug"]) == 4
