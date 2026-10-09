import cv2
import mediapipe as mp
import math
import numpy as np
from pathlib import Path
from threading import Lock


# =========================================================
# MEDIAPIPE FACE DETECTION
# =========================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "face_landmarker.task"
)
_LANDMARKER = None
_LANDMARKER_LOCK = Lock()


def _detect_face_landmarks(mp_image):
    global _LANDMARKER
    with _LANDMARKER_LOCK:
        if _LANDMARKER is None:
            options = mp.tasks.vision.FaceLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
                num_faces=4,
            )
            _LANDMARKER = mp.tasks.vision.FaceLandmarker.create_from_options(options)
        results = _LANDMARKER.detect(mp_image)
    return results.face_landmarks


def estimate_visible_skin_appearance(image, landmarks):
    image_height, image_width = image.shape[:2]
    points = np.array([
        [int(point.x * image_width), int(point.y * image_height)]
        for point in landmarks
    ], dtype=np.int32)
    face_height = float(np.linalg.norm(points[10] - points[152]))
    face_width = float(np.linalg.norm(points[234] - points[454]))
    if face_height <= 0 or face_width <= 0:
        return {
            "label": "Unable to estimate visible skin appearance",
            "confidence": "Low",
            "visible_shine_percent": None,
            "estimated_skin_type": "Unavailable",
            "skin_type_confidence": "Low",
            "skin_tone": "unavailable",
            "skin_tone_label": "Unable to estimate complexion",
            "skin_tone_confidence": "Low",
        }

    shine_mask = np.zeros((image_height, image_width), dtype=np.uint8)
    cheek_mask = np.zeros((image_height, image_width), dtype=np.uint8)
    cheek_radius = (max(1, int(face_width * 0.075)), max(1, int(face_height * 0.045)))
    for index in (116, 345):
        center = tuple(points[index])
        cv2.ellipse(shine_mask, center, cheek_radius, 0, 0, 360, 255, -1)
        cv2.ellipse(cheek_mask, center, cheek_radius, 0, 0, 360, 255, -1)

    forehead_center = (
        int((points[54][0] + points[284][0]) / 2),
        int((points[54][1] + points[284][1]) / 2 + face_height * 0.08),
    )
    forehead_radius = (max(1, int(face_width * 0.11)), max(1, int(face_height * 0.04)))
    cv2.ellipse(shine_mask, forehead_center, forehead_radius, 0, 0, 360, 255, -1)

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    shine_pixels = hsv_image[shine_mask > 0]
    cheek_pixels = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)[:, :, 0][cheek_mask > 0]
    if not len(shine_pixels) or not len(cheek_pixels):
        return {
            "label": "Unable to estimate visible skin appearance",
            "confidence": "Low",
            "visible_shine_percent": None,
            "estimated_skin_type": "Unavailable",
            "skin_type_confidence": "Low",
            "skin_tone": "unavailable",
            "skin_tone_label": "Unable to estimate complexion",
            "skin_tone_confidence": "Low",
        }

    brightness = shine_pixels[:, 2]
    saturation = shine_pixels[:, 1]
    shine_cutoff = max(170, int(np.percentile(brightness, 85)))
    shine_ratio = float(np.mean((brightness >= shine_cutoff) & (saturation <= 105)))
    shine_percent = round(shine_ratio * 100, 1)

    if shine_ratio >= 0.12:
        label = "Oily-leaning visible shine"
        estimated_skin_type = "Oily-leaning appearance"
    elif shine_ratio >= 0.045:
        label = "Combination-leaning visible shine"
        estimated_skin_type = "Combination-leaning appearance"
    else:
        label = "Low visible shine"
        estimated_skin_type = "Balanced/low-shine appearance"

    median_lightness = float(np.median(cheek_pixels)) * (100 / 255)
    if median_lightness >= 68:
        skin_tone = "fair"
    elif median_lightness >= 48:
        skin_tone = "medium"
    else:
        skin_tone = "deep"
    return {
        "label": label,
        "confidence": "Low",
        "visible_shine_percent": shine_percent,
        "estimated_skin_type": estimated_skin_type,
        "skin_type_confidence": "Low",
        "skin_tone": skin_tone,
        "skin_tone_label": f"{skin_tone.title()} complexion estimate",
        "skin_tone_confidence": "Low",
    }


def analyze_face(image_path):
    image = cv2.imread(str(image_path))
    if image is None:
        return {"success": False, "message": "Could not read the captured image."}

    if not MODEL_PATH.exists():
        return {"success": False, "message": "The face landmark model is missing."}

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    face_landmarks = _detect_face_landmarks(mp_image)

    if not face_landmarks:
        return {
            "success": True,
            "face_detected": False,
            "face_count": 0,
            "message": "No face detected. Please capture a clear, front-facing photo.",
        }

    landmarks = face_landmarks[0]

    def distance(first, second):
        return math.hypot(first.x - second.x, first.y - second.y)

    face_length = distance(landmarks[10], landmarks[152])
    forehead_width = distance(landmarks[54], landmarks[284])
    cheekbone_width = distance(landmarks[234], landmarks[454])
    jaw_width = distance(landmarks[172], landmarks[397])
    width_length_ratio = cheekbone_width / face_length if face_length else 0
    jaw_cheek_ratio = jaw_width / cheekbone_width if cheekbone_width else 0
    forehead_cheek_ratio = forehead_width / cheekbone_width if cheekbone_width else 0

    if width_length_ratio < 0.72:
        face_shape = "Oblong"
    elif width_length_ratio > 0.88:
        face_shape = "Square" if jaw_cheek_ratio > 0.85 else "Round"
    elif jaw_cheek_ratio < 0.72:
        face_shape = "Heart"
    elif forehead_cheek_ratio < 0.78:
        face_shape = "Diamond"
    else:
        face_shape = "Oval"

    skin_appearance = estimate_visible_skin_appearance(image, landmarks)

    return {
        "success": True,
        "face_detected": True,
        "face_count": len(face_landmarks),
        "face_shape": face_shape,
        "face_ratio": round(width_length_ratio, 2),
        "skin_appearance": skin_appearance,
        "landmarks": [{"x": point.x, "y": point.y} for point in landmarks],
        "message": "Face detected successfully.",
    }