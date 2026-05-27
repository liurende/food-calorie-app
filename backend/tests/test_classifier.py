import numpy as np
import cv2
import os
from ai.classifier import classify_food


def test_classify_simulated():
    """Test simulated classification path."""
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(img, (150, 150), 100, (200, 180, 160), -1)
    path = "test_food_classify.jpg"
    cv2.imwrite(path, img)

    result = classify_food(path)
    assert result["name"]
    assert result["confidence"] >= 0.70
    assert result["source"] == "simulated"
    os.remove(path)
