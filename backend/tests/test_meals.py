from fastapi.testclient import TestClient
from datetime import date
from main import app
from database import init_db

client = TestClient(app)
init_db()


def test_create_and_list_meal():
    payload = {
        "user_id": "test_user",
        "meal_type": "lunch",
        "total_calories": 486.0,
        "items": [
            {"name": "宫保鸡丁", "weight_g": 320.0, "calories": 268.0,
             "protein_g": 32.0, "carbs_g": 5.8, "fat_g": 4.5, "confidence": 0.92},
            {"name": "白米饭", "weight_g": 200.0, "calories": 218.0,
             "protein_g": 5.2, "carbs_g": 51.8, "fat_g": 0.6, "confidence": 0.96},
        ],
    }
    resp = client.post("/api/meals", json=payload)
    assert resp.status_code == 201
    meal_id = resp.json()["id"]

    resp = client.get(f"/api/meals?user_id=test_user&date={date.today().isoformat()}")
    assert resp.status_code == 200
    meals = resp.json()
    assert len(meals) >= 1

    resp = client.delete(f"/api/meals/{meal_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"
