import numpy as np
import cv2
import os
import pytest
from engine.feature_matching import extract_features, match_features, get_matched_points


@pytest.fixture
def two_test_images():
    """Create two images of the same scene from slightly different viewpoints."""
    # Use deterministic pattern: grid of textured blobs that SIFT can match
    rng = np.random.RandomState(42)
    img1 = np.zeros((300, 300, 3), dtype=np.uint8)
    img2 = np.zeros((300, 300, 3), dtype=np.uint8)

    # Draw same blobs in both images, offset by (10, 5)
    for i in range(30):
        cx, cy = rng.randint(60, 240), rng.randint(60, 240)
        r = rng.randint(4, 10)
        brightness = rng.randint(150, 255)
        color = (brightness, brightness - 20, brightness - 40)

        # Image 1: original position
        cv2.circle(img1, (cx, cy), r, color, -1)
        cv2.circle(img1, (cx, cy), r, (255, 255, 255), 1)

        # Image 2: shifted position (simulating camera movement)
        cv2.circle(img2, (cx + 10, cy + 5), r, color, -1)
        cv2.circle(img2, (cx + 10, cy + 5), r, (255, 255, 255), 1)

    # Add background texture
    for x in range(0, 300, 8):
        for y in range(0, 300, 8):
            val = 40 + (x + y) % 30
            img1[y:min(y+4, 300), x:min(x+4, 300)] = (val, val, val)
            img2[y:min(y+4, 300), x:min(x+4, 300)] = (val, val, val)

    path1 = "test_img1.jpg"
    path2 = "test_img2.jpg"
    cv2.imwrite(path1, img1)
    cv2.imwrite(path2, img2)
    yield path1, path2
    os.remove(path1)
    os.remove(path2)


def test_extract_and_match(two_test_images):
    path1, path2 = two_test_images
    kp1, desc1 = extract_features(path1)
    kp2, desc2 = extract_features(path2)
    assert len(kp1) > 0
    assert len(kp2) > 0

    matches = match_features(desc1, desc2)
    assert len(matches) > 0

    pts1, pts2 = get_matched_points(kp1, kp2, matches)
    assert pts1.shape == pts2.shape
    assert pts1.shape[0] == len(matches)
