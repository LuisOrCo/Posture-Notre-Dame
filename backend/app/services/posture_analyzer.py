import math
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.services.pose_detector import detector_instance
from app.database import posture_logs_collection

ANGLE_THRESHOLD_DEGREES = 15.0


def calculate_neck_shoulder_angle(landmarks) -> float:
    # Landmark 0: Nose, 7: Left Ear, 8: Right Ear, 11: Left Shoulder, 12: Right Shoulder
    left_ear = landmarks[7]
    right_ear = landmarks[8]
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    # Punto medio entre las orejas (cabeza / cuello superior)
    ear_mid_x = (left_ear.x + right_ear.x) / 2.0
    ear_mid_y = (left_ear.y + right_ear.y) / 2.0

    # Punto medio entre los hombros
    shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2.0
    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2.0

    # Vector de inclinación
    dx = abs(ear_mid_x - shoulder_mid_x)
    dy = abs(ear_mid_y - shoulder_mid_y)

    if dy == 0:
        return 90.0

    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)

    return round(angle_deg, 1)


def analyze_posture(image_base64: str, username: Optional[str] = None) -> Dict[str, Any]:
    try:
        img = detector_instance.decode_base64_image(image_base64)
    except Exception as e:
        raise ValueError(f"Error decodificando la imagen: {str(e)}")

    landmarks = detector_instance.detect_landmarks(img)

    if not landmarks:
        return {
            "posture": "bad",
            "angle": 0.0,
            "message": "No se detectó silueta de persona o puntos de pose en el frame.",
        }

    angle = calculate_neck_shoulder_angle(landmarks)
    posture_status = "good" if angle <= ANGLE_THRESHOLD_DEGREES else "bad"
    message = (
        "Postura adecuada. Mantén la alineación ergonómica."
        if posture_status == "good"
        else f"Inclinación de cabeza/cuello excesiva ({angle}° > {ANGLE_THRESHOLD_DEGREES}°). Corrige la postura."
    )

    now = datetime.now(timezone.utc)
    if username:
        log_doc = {
            "username": username,
            "posture": posture_status,
            "angle": angle,
            "created_at": now,
        }
        posture_logs_collection.insert_one(log_doc)

    return {
        "posture": posture_status,
        "angle": angle,
        "message": message,
    }


def get_posture_stats(username: Optional[str] = None) -> Dict[str, Any]:
    query = {}
    if username:
        query["username"] = username

    logs = list(posture_logs_collection.find(query))
    total_samples = len(logs)

    if total_samples == 0:
        return {
            "total_samples": 0,
            "good_posture_count": 0,
            "bad_posture_count": 0,
            "good_percentage": 0.0,
            "bad_percentage": 0.0,
        }

    good_count = sum(1 for log in logs if log.get("posture") == "good")
    bad_count = total_samples - good_count

    good_pct = round((good_count / total_samples) * 100.0, 1)
    bad_pct = round((bad_count / total_samples) * 100.0, 1)

    return {
        "total_samples": total_samples,
        "good_posture_count": good_count,
        "bad_posture_count": bad_count,
        "good_percentage": good_pct,
        "bad_percentage": bad_pct,
    }
