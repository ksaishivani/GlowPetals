# ============================================================
# GLOWPETALS - FACIAL LANDMARK MODULE
# ============================================================

import cv2
import mediapipe as mp
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    r"C:\Users\HP\Desktop\GlowPetals_AI"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "face_landmarker.task"
)


# ============================================================
# DETECT FACIAL LANDMARKS
# ============================================================

def detect_landmarks(image_path):

    print("\n🔍 Loading image...")

    # Read image
    image = cv2.imread(str(image_path))

    if image is None:

        print("❌ Could not read image.")
        print("Image path:", image_path)

        return None

    print("✅ Image loaded successfully!")

    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # Create MediaPipe image
    # --------------------------------------------------------

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_image
    )

    print("✅ MediaPipe image created!")

    # --------------------------------------------------------
    # MediaPipe options
    # --------------------------------------------------------

    base_options = mp.tasks.BaseOptions(
        model_asset_path=str(MODEL_PATH)
    )

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=1
    )

    # --------------------------------------------------------
    # Create Face Landmarker
    # --------------------------------------------------------

    print("🔄 Creating Face Landmarker...")

    landmarker = (
        mp.tasks.vision.FaceLandmarker
        .create_from_options(options)
    )

    print("✅ Face Landmarker created!")

    # --------------------------------------------------------
    # Detect landmarks
    # --------------------------------------------------------

    result = landmarker.detect(mp_image)

    landmarker.close()

    # --------------------------------------------------------
    # Check result
    # --------------------------------------------------------

    if len(result.face_landmarks) == 0:

        print("❌ No facial landmarks detected.")

        return None

    print("✅ Detection completed!")

    print(
        "📍 Landmarks detected:",
        len(result.face_landmarks[0])
    )

    # Return both image and landmarks
    return image, result.face_landmarks[0]