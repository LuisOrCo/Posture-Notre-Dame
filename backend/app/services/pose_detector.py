import base64
import os
import numpy as np
import cv2
import mediapipe as mp

try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core import base_options
    HAS_MEDIAPIPE_TASKS = True
except Exception:
    HAS_MEDIAPIPE_TASKS = False


class LandmarkPoint:
    def __init__(self, x: float, y: float, visibility: float = 0.9):
        self.x = x
        self.y = y
        self.visibility = visibility


class PoseDetector:
    def __init__(self, model_path: str = "pose_landmarker.task"):
        self.model_path = model_path
        self.landmarker = None
        
        if HAS_MEDIAPIPE_TASKS and os.path.exists(model_path):
            try:
                options = vision.PoseLandmarkerOptions(
                    base_options=base_options.BaseOptions(model_asset_path=model_path),
                    running_mode=vision.RunningMode.IMAGE,
                )
                self.landmarker = vision.PoseLandmarker.create_from_options(options)
            except Exception:
                self.landmarker = None

        # Cargar clasificador de rostros en OpenCV como fallback geométrico postural
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if os.path.exists(face_cascade_path):
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        else:
            self.face_cascade = None

    def decode_base64_image(self, base64_str: str) -> np.ndarray:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        
        image_bytes = base64.b64decode(base64_str)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("No se pudo decodificar la imagen enviada.")
        return img

    def detect_landmarks(self, img_bgr: np.ndarray):
        h, w, _ = img_bgr.shape

        # 1. Intentar inferencia con MediaPipe PoseLandmarker si el modelo .task está presente
        if self.landmarker is not None:
            try:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
                result = self.landmarker.detect(mp_image)
                if result and result.pose_landmarks and len(result.pose_landmarks) > 0:
                    landmarks = result.pose_landmarks[0]
                    return [LandmarkPoint(lm.x, lm.y, getattr(lm, "visibility", 0.9)) for lm in landmarks]
            except Exception:
                pass

        # 2. Fallback de detección postural mediante OpenCV Haar Cascade si no se dispone del archivo de modelo
        if self.face_cascade is not None:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR_GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            if len(faces) > 0:
                # Tomar el rostro con mayor área
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                (fx, fy, fw, fh) = faces[0]

                # Construir una representación simulada de 33 puntos con orejas y hombros según la geometría facial
                landmarks = [LandmarkPoint(0.5, 0.5)] * 33
                
                # Orejas a los lados del rostro
                left_ear_x = (fx + fw * 0.15) / w
                right_ear_x = (fx + fw * 0.85) / w
                ear_y = (fy + fh * 0.5) / h

                # Hombros estimados bajo el rostro
                left_shoulder_x = (fx - fw * 0.4) / w
                right_shoulder_x = (fx + fw * 1.4) / w
                shoulder_y = (fy + fh * 1.8) / h

                landmarks[7] = LandmarkPoint(left_ear_x, ear_y)
                landmarks[8] = LandmarkPoint(right_ear_x, ear_y)
                landmarks[11] = LandmarkPoint(left_shoulder_x, shoulder_y)
                landmarks[12] = LandmarkPoint(right_shoulder_x, shoulder_y)

                return landmarks

        return None


detector_instance = PoseDetector()
