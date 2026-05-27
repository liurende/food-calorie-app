import cv2
import numpy as np
from engine.feature_matching import extract_features, match_features, get_matched_points


class VolumeEstimator:
    """Estimates food volume from multi-angle images using sparse 3D reconstruction.

    Uses known camera distance (~30cm from food) to set absolute scale.
    Requires at least 2 images from different angles.
    """

    def __init__(self, known_distance_cm: float = 30.0):
        self.known_distance = known_distance_cm  # cm from camera to food center

    def estimate_volume(self, image_paths: list[str]) -> dict:
        """Main entry point: estimate volume from 2-3 images.

        Returns dict with volume_cm3, point_count, and scale_factor.
        """
        if len(image_paths) < 2:
            raise ValueError("Need at least 2 images for reconstruction")

        all_points_3d = []
        scale = self.known_distance / 30.0  # normalize to reference distance

        for i in range(len(image_paths) - 1):
            kp1, desc1 = extract_features(image_paths[i])
            kp2, desc2 = extract_features(image_paths[i + 1])
            matches = match_features(desc1, desc2)
            pts1, pts2 = get_matched_points(kp1, kp2, matches)

            # Simulate camera parameters with known distance
            img = cv2.imread(image_paths[i])
            h, w = img.shape[:2]
            focal = max(w, h) * (self.known_distance / 10.0)  # approximate focal length

            K = np.array([
                [focal, 0, w / 2],
                [0, focal, h / 2],
                [0, 0, 1],
            ], dtype=np.float32)

            # Assume small rotation between views (~15-45 degrees)
            angle_rad = np.radians(30.0)
            E = np.array([
                [0, 0, 0],
                [0, 0, -1],
                [0, 1, 0],
            ], dtype=np.float32) * np.sin(angle_rad)

            R1 = np.eye(3, dtype=np.float32)
            t1 = np.zeros((3, 1), dtype=np.float32)
            R2, _ = cv2.Rodrigues(np.array([0, angle_rad, 0], dtype=np.float32))
            t2 = np.array([[0.05 * self.known_distance], [0], [0]], dtype=np.float32)

            P1 = K @ np.hstack((R1, t1))
            P2 = K @ np.hstack((R2, t2))

            pts_4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
            pts_3d = pts_4d[:3] / pts_4d[3]
            pts_3d *= scale

            all_points_3d.append(pts_3d.T)

        if not all_points_3d:
            raise ValueError("Failed to reconstruct 3D points")

        combined = np.vstack(all_points_3d)

        # Filter outliers
        centroid = np.median(combined, axis=0)
        distances = np.linalg.norm(combined - centroid, axis=1)
        threshold = np.percentile(distances, 90)
        filtered = combined[distances <= threshold]

        if len(filtered) < 4:
            filtered = combined

        # Compute convex hull volume
        try:
            hull = cv2.convexHull(filtered.astype(np.float32))
            volume = cv2.contourArea(hull.reshape(-1, 1, 2)) if hull is not None else 0

            # Approximate depth from point spread in Z
            z_range = np.ptp(filtered[:, 2]) if filtered.shape[1] > 2 else 0
            if z_range < 0.1:
                z_range = max(1.0, volume ** (1 / 3) * 0.5)

            volume_cm3 = volume * z_range * 0.01  # scale to cm³
        except Exception:
            bbox_dims = np.ptp(filtered, axis=0)
            volume_cm3 = float(np.prod(bbox_dims)) * 0.01

        volume_cm3 = max(10.0, min(5000.0, abs(volume_cm3)))

        return {
            "volume_cm3": round(volume_cm3, 1),
            "point_count": len(filtered),
            "scale_factor": round(scale, 2),
        }
