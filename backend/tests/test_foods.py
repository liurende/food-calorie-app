from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_search_foods():
    response = client.get("/api/foods/search?q=鸡")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any("鸡" in r["name"] for r in results)


def test_search_foods_empty():
    response = client.get("/api/foods/search?q=xyznotfound")
    assert response.status_code == 200
    assert response.json() == []
