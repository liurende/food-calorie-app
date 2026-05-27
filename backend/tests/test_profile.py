from fastapi.testclient import TestClient
from main import app
from database import init_db

client = TestClient(app)
init_db()


def test_get_profile_empty():
    resp = client.get("/api/profile?user_id=nobody")
    assert resp.status_code == 200
    data = resp.json()
    assert data["profile"] is None
    assert data["bmr"] is None


def test_update_and_get_profile():
    payload = {
        "user_id": "test_user",
        "name": "测试",
        "gender": "male",
        "age": 30,
        "height_cm": 175.0,
        "weight_kg": 70.0,
        "activity_level": "moderate",
    }
    resp = client.put("/api/profile", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["profile"]["gender"] == "male"
    assert data["bmr"] > 0
    assert data["tdee"] > data["bmr"]

    # Verify GET returns same data
    resp2 = client.get("/api/profile?user_id=test_user")
    assert resp2.status_code == 200
    assert resp2.json()["bmr"] == data["bmr"]


def test_bmr_female():
    payload = {
        "user_id": "test_female",
        "name": "小红",
        "gender": "female",
        "age": 25,
        "height_cm": 160.0,
        "weight_kg": 55.0,
        "activity_level": "light",
    }
    resp = client.put("/api/profile", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # BMR for female should be lower than male with same stats
    assert data["bmr"] > 0
    assert data["tdee"] > data["bmr"]
