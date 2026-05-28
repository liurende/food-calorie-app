import numpy as np
import cv2
import os
import pytest
from ai.classifier import classify_food


def _make_test_image(path: str):
    """Create a simple food-like image for testing."""
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(img, (150, 150), 100, (200, 180, 160), -1)
    cv2.imwrite(path, img)


def test_classify_without_api_key(monkeypatch):
    """Without ANTHROPIC_AUTH_TOKEN, should return unknown gracefully."""
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    path = "test_food_no_key.jpg"
    _make_test_image(path)

    result = classify_food(path)
    assert result["name"] == "unknown"
    assert result["confidence"] == 0.0
    assert result["source"] == "none"
    os.remove(path)


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_AUTH_TOKEN"),
    reason="ANTHROPIC_AUTH_TOKEN not set",
)
def test_classify_with_api_key():
    """With API key, should return a food name from Haiku."""
    path = "test_food_real.jpg"
    _make_test_image(path)

    result = classify_food(path)
    assert result["name"]
    assert result["confidence"] > 0
    assert result["source"] == "haiku"
    os.remove(path)
