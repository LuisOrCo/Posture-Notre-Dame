import unittest
import base64
import io
from unittest.mock import MagicMock, patch
import numpy as np
from PIL import Image

from app.services.pose_detector import detector_instance
from app.services.posture_analyzer import (
    calculate_neck_shoulder_angle,
    analyze_posture,
    get_posture_stats,
)
from app.api.routes.posture import analyze_posture_endpoint, get_posture_stats_endpoint
from app.schemas.posture import PostureRequest


def create_dummy_base64_image() -> str:
    # Crear imagen sintética RGB 100x100
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    return "data:image/jpeg;base64," + base64.b64encode(byte_im).decode("utf-8")


class MockLandmark:
    def __init__(self, x: float, y: float, visibility: float = 0.9):
        self.x = x
        self.y = y
        self.visibility = visibility


class TestPostureDetectionAndAnalyzer(unittest.TestCase):

    def test_decode_base64_image(self):
        b64_str = create_dummy_base64_image()
        img_arr = detector_instance.decode_base64_image(b64_str)
        self.assertIsInstance(img_arr, np.ndarray)
        self.assertEqual(img_arr.shape[0], 100)
        self.assertEqual(img_arr.shape[1], 100)

    def test_calculate_neck_shoulder_angle_good(self):
        # Orejas en (0.5, 0.2), Hombros alineados verticalmente en (0.5, 0.5) => ángulo 0.0°
        landmarks = [MockLandmark(0, 0)] * 33
        landmarks[7] = MockLandmark(0.48, 0.2)   # Left ear
        landmarks[8] = MockLandmark(0.52, 0.2)   # Right ear
        landmarks[11] = MockLandmark(0.40, 0.5)  # Left shoulder
        landmarks[12] = MockLandmark(0.60, 0.5)  # Right shoulder

        angle = calculate_neck_shoulder_angle(landmarks)
        self.assertEqual(angle, 0.0)

    def test_calculate_neck_shoulder_angle_bad(self):
        # Orejas desplazadas horizontalmente hacia adelante => (0.7, 0.2), Hombros en (0.5, 0.5)
        landmarks = [MockLandmark(0, 0)] * 33
        landmarks[7] = MockLandmark(0.68, 0.2)   # Left ear
        landmarks[8] = MockLandmark(0.72, 0.2)   # Right ear
        landmarks[11] = MockLandmark(0.40, 0.5)  # Left shoulder
        landmarks[12] = MockLandmark(0.60, 0.5)  # Right shoulder

        angle = calculate_neck_shoulder_angle(landmarks)
        self.assertGreater(angle, 15.0)

    @patch("app.services.posture_analyzer.detector_instance")
    def test_analyze_posture_good(self, mock_detector):
        mock_detector.decode_base64_image.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        landmarks = [MockLandmark(0, 0)] * 33
        landmarks[7] = MockLandmark(0.48, 0.2)
        landmarks[8] = MockLandmark(0.52, 0.2)
        landmarks[11] = MockLandmark(0.40, 0.5)
        landmarks[12] = MockLandmark(0.60, 0.5)
        mock_detector.detect_landmarks.return_value = landmarks

        res = analyze_posture("dummy_base64")
        self.assertEqual(res["posture"], "good")
        self.assertEqual(res["angle"], 0.0)

    @patch("app.services.posture_analyzer.detector_instance")
    def test_analyze_posture_bad(self, mock_detector):
        mock_detector.decode_base64_image.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        landmarks = [MockLandmark(0, 0)] * 33
        landmarks[7] = MockLandmark(0.68, 0.2)
        landmarks[8] = MockLandmark(0.72, 0.2)
        landmarks[11] = MockLandmark(0.40, 0.5)
        landmarks[12] = MockLandmark(0.60, 0.5)
        mock_detector.detect_landmarks.return_value = landmarks

        res = analyze_posture("dummy_base64")
        self.assertEqual(res["posture"], "bad")
        self.assertGreater(res["angle"], 15.0)

    @patch("app.services.posture_analyzer.posture_logs_collection")
    def test_get_posture_stats(self, mock_logs_coll):
        mock_logs_coll.find.return_value = [
            {"posture": "good", "angle": 10.0},
            {"posture": "good", "angle": 12.0},
            {"posture": "bad", "angle": 22.0},
        ]

        stats = get_posture_stats(username="testuser")
        self.assertEqual(stats["total_samples"], 3)
        self.assertEqual(stats["good_posture_count"], 2)
        self.assertEqual(stats["bad_posture_count"], 1)
        self.assertEqual(stats["good_percentage"], 66.7)
        self.assertEqual(stats["bad_percentage"], 33.3)

    @patch("app.api.routes.posture.analyze_posture")
    def test_analyze_posture_endpoint(self, mock_analyze):
        mock_analyze.return_value = {
            "posture": "good",
            "angle": 12.5,
            "message": "Postura adecuada.",
        }

        req = PostureRequest(image=create_dummy_base64_image())
        res = analyze_posture_endpoint(req, current_user=None)
        self.assertEqual(res["posture"], "good")
        self.assertEqual(res["angle"], 12.5)


if __name__ == "__main__":
    unittest.main()
