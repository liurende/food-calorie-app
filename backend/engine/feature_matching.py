import cv2
import numpy as np


def extract_features(image_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Extract SIFT keypoints and descriptors from an image."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    if descriptors is None or len(keypoints) < 10:
        raise ValueError(f"Too few features found in {image_path}")
    return keypoints, descriptors


def match_features(desc1: np.ndarray, desc2: np.ndarray) -> list[cv2.DMatch]:
    """Match SIFT descriptors between two images using FLANN."""
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(desc1, desc2, k=2)
    good = [m for m, n in matches if m.distance < 0.7 * n.distance]
    return good


def get_matched_points(
    kp1: list[cv2.KeyPoint], kp2: list[cv2.KeyPoint], matches: list[cv2.DMatch]
) -> tuple[np.ndarray, np.ndarray]:
    """Return matched point coordinates from two images."""
    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])
    return pts1, pts2
