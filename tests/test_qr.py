import httpx

HEADERS = {"X-Admin-Token": "test-token"}


async def test_qr_returns_png(client: httpx.AsyncClient) -> None:
    await client.post(
        "/api/links",
        json={"target": "https://example.com/", "slug": "qr"},
        headers=HEADERS,
    )

    r = await client.get("/qr/qr")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content.startswith(b"\x89PNG\r\n\x1a\n")


async def test_qr_404_for_missing_slug(client: httpx.AsyncClient) -> None:
    assert (await client.get("/qr/nope")).status_code == 404
