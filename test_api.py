from fastapi.testclient import TestClient
from main import app
from data import HERO_ITEM, HERO_SELLER_ZIP, HERO_BIDS

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_route_hero_example():
    r = client.post("/route", json={
        "item": HERO_ITEM, "seller_zip": HERO_SELLER_ZIP, "bids": HERO_BIDS})
    assert r.status_code == 200
    assert [b["maker_id"] for b in r.json()] == ["B_chicago", "C_dallas", "A_los_angeles"]


def test_route_rejects_bad_zip():
    r = client.post("/route", json={
        "item": HERO_ITEM, "seller_zip": "1234", "bids": HERO_BIDS})
    assert r.status_code == 422