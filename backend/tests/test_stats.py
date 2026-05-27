from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_stats_empty():
    response = client.get("/api/stats?user_id=test_user&range=daily")
    assert response.status_code == 200
    data = response.json()
    assert data["total_calories"] == 0
    assert data["meals"] == []
