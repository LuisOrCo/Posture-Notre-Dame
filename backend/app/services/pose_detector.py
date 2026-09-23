import base64
import os
import urllib.request
import logging
import numpy as np
import cv2
import mediapipe as mp

logger = logging.getLogger(__name__)

try:
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core import base_options
    HAS_MEDIAPIPE_TASKS = True
except Exception as e:
    logger.warning(f"MediaPipe Tasks no disponible: {e}")
    HAS_MEDIAPIPE_TASKS = False

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"


class LandmarkPoint:
    def __init__(self, x: float, y: float, visibility: float = 0.9):
        self.x = x
        self.y = y
        self.visibility = visibility


class PoseDetector:
    def __init__(self, model_filename: str = "pose_landmarker.task"):
        # Buscar el archivo en backend/models/, raíz del backend, directorio actual o /tmp
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
        models_dir = os.path.join(backend_dir, "models")
        tmp_path = os.path.join("/tmp", model_filename)
        
        candidate_paths = [
            os.path.join(models_dir, model_filename),
            os.path.join(backend_dir, model_filename),
            os.path.join(current_dir, model_filename),
            os.path.abspath(model_filename),
            tmp_path,
        ]
        
        self.model_path = None
        for path in candidate_paths:
            if os.path.exists(path):
                self.model_path = path
                break

        # Descargar el modelo automáticamente a /tmp si no existe en ninguna de las rutas (compatible con Vercel)
        if not self.model_path or not os.path.exists(self.model_path):
            self.model_path = tmp_path
            try:
                logger.info(f"Descargando modelo de pose desde {MODEL_URL}...")
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                urllib.request.urlretrieve(MODEL_URL, self.model_path)
                logger.info(f"Modelo guardado exitosamente en: {self.model_path}")
            except Exception as e:
                logger.error(f"Error descargando el modelo MediaPipe: {e}")

        self.landmarker = None
        if HAS_MEDIAPIPE_TASKS and os.path.exists(self.model_path):
            try:
                options = vision.PoseLandmarkerOptions(
                    base_options=base_options.BaseOptions(model_asset_path=self.model_path),
                    running_mode=vision.RunningMode.IMAGE,
                )
                self.landmarker = vision.PoseLandmarker.create_from_options(options)
                logger.info("MediaPipe PoseLandmarker inicializado correctamente.")
            except Exception as e:
                logger.error(f"Error inicializando PoseLandmarker: {e}")
                self.landmarker = None

        # Cargar clasificador de rostros en OpenCV como fallback
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

        # 1. Inferencia precisa con MediaPipe PoseLandmarker
        if self.landmarker is not None:
            try:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
                result = self.landmarker.detect(mp_image)
                if result and result.pose_landmarks and len(result.pose_landmarks) > 0:
                    landmarks = result.pose_landmarks[0]
                    return [LandmarkPoint(lm.x, lm.y, getattr(lm, "visibility", 0.9)) for lm in landmarks]
            except Exception as e:
                logger.warning(f"Excepción en MediaPipe PoseLandmarker: {e}")

        # 2. Fallback de detección postural mediante OpenCV Haar Cascade si no se detecta por landmarker
        if self.face_cascade is not None:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(30, 30)
            )
            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                (fx, fy, fw, fh) = faces[0]

                landmarks = [LandmarkPoint(0.5, 0.5)] * 33
                
                left_ear_x = (fx + fw * 0.15) / w
                right_ear_x = (fx + fw * 0.85) / w
                ear_y = (fy + fh * 0.5) / h

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
