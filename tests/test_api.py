from fastapi import status
from fastapi.testclient import TestClient

from douglas.api import app

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == status.HTTP_200_OK


def test_crawl_url():
    res = client.post(
        "/api/crawl",
        json={"url": "https://www.douglas.de/de/p/3001055831?variant=077163"},
    )
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["ean"] == "3605971937811"
