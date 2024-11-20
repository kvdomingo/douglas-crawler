import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from douglas.api import app

transport = ASGITransport(app=app)
client = AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio(loop_scope="module")
async def test_health_check():
    res = await client.get("/api/health")
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.asyncio(loop_scope="module")
async def test_crawl_url():
    res = await client.post(
        "/api/crawl",
        json={"url": "https://www.douglas.de/de/p/3001055831?variant=077163"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["ean"] == "3605971937811"


@pytest.mark.asyncio(loop_scope="module")
async def test_list_products():
    res = await client.get("/api/products")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["page_size"] > 0
    assert isinstance(data["items"], list)


@pytest.mark.asyncio(loop_scope="module")
async def test_get_nonexistent_product():
    res = await client.get("/api/products/000")
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(loop_scope="module")
async def test_get_existing_product():
    res = await client.get("/api/products/3605971937811")
    assert res.status_code == status.HTTP_200_OK
