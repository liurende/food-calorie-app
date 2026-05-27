from fastapi.testclient import TestClient
from main import app
from database import init_db
from seed_data import seed

client = TestClient(app)
init_db()
seed()


def test_recognize_endpoint():
    """Test full recognition pipeline with test images."""
    import numpy as np
    import cv2

    img1 = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.ellipse(img1, (200, 210), (120, 100), 0, 0, 360, (200, 180, 160), -1)
    for i in range(30):
        cv2.circle(img1, (np.random.randint(100, 300), np.random.randint(130, 290)),
                   np.random.randint(3, 10), (255, 230, 200), -1)

    img2 = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.ellipse(img2, (210, 215), (120, 100), 0, 0, 360, (200, 180, 160), -1)
    for i in range(30):
        cv2.circle(img2, (np.random.randint(110, 310), np.random.randint(135, 295)),
                   np.random.randint(3, 10), (255, 230, 200), -1)

    path1 = "test_recognize_1.jpg"
    path2 = "test_recognize_2.jpg"
    cv2.imwrite(path1, img1)
    cv2.imwrite(path2, img2)

    import os
    resp = client.post("/api/recognize", json={
        "image_paths": [os.path.abspath(path1), os.path.abspath(path2)],
        "known_distance_cm": 30.0,
    })
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert "name" in results[0]
    assert results[0]["weight_g"] > 0
    assert results[0]["calories"] > 0

    os.remove(path1)
    os.remove(path2)
