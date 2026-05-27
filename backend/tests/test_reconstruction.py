import numpy as np
import cv2
import os
import pytest
from engine.reconstruction import VolumeEstimator


@pytest.fixture
def two_angle_images():
    """Two images of a simulated food blob from slightly different angles."""
    def make_food_image(offset_x=0):
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        # Draw an ellipse to simulate food on a plate
        cv2.ellipse(img, (200 + offset_x, 210), (120, 100), 0, 0, 360, (200, 180, 160), -1)
        cv2.ellipse(img, (200 + offset_x, 210), (120, 100), 0, 0, 360, (255, 230, 200), 2)
        # Add some texture with circles
        for _ in range(20):
            cx = np.random.randint(100 + offset_x, 300 + offset_x)
            cy = np.random.randint(130, 290)
            r = np.random.randint(3, 8)
            colors = [(180, 160, 140), (220, 200, 180), (160, 140, 120)]
            color = colors[np.random.randint(0, len(colors))]
            cv2.circle(img, (cx, cy), r, color, -1)
        return img

    img1 = make_food_image(0)
    img2 = make_food_image(15)

    path1 = "test_food_1.jpg"
    path2 = "test_food_2.jpg"
    cv2.imwrite(path1, img1)
    cv2.imwrite(path2, img2)
    yield [path1, path2]
    os.remove(path1)
    os.remove(path2)


def test_volume_estimation(two_angle_images):
    estimator = VolumeEstimator(known_distance_cm=30.0)
    result = estimator.estimate_volume(two_angle_images)
    assert "volume_cm3" in result
    assert result["volume_cm3"] > 0
    assert result["point_count"] > 0
