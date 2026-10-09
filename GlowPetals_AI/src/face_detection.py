# %%
import sys
import cv2
import mediapipe as mp
from pathlib import Path

print("Python:", sys.executable)
print("OpenCV:", cv2.__version__)
print("MediaPipe:", mp.__version__)


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = Path(
    r"C:\Users\HP\Desktop\GlowPetals_AI\models\blaze_face_short_range.tflite"
)

IMAGE_PATH = Path(
    r"C:\Users\HP\Desktop\GlowPetals_AI\assets\test_face.jpg"
)


# ============================================================
# FACE DETECTION
# ============================================================

def detect_faces(image_path):

    print("\n🔍 Checking image...")

    image = cv2.imread(str(image_path))

    if image is None:
        print("❌ Could not read image")
        return None

    print("✅ Image loaded successfully!")

    # BGR → RGB
    rgb_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    print("✅ RGB conversion completed!")

    # MediaPipe image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_image
    )

    print("✅ MediaPipe image created!")

    # Model
    base_options = mp.tasks.BaseOptions(
        model_asset_path=str(MODEL_PATH)
    )

    print("✅ Model options created!")

    options = mp.tasks.vision.FaceDetectorOptions(
        base_options=base_options,
        min_detection_confidence=0.2
    )

    print("✅ Detector options created!")

    detector = mp.tasks.vision.FaceDetector.create_from_options(
        options
    )

    print("✅ Face detector created!")

    # Detection
    result = detector.detect(mp_image)

    print("✅ Face detection completed!")

    detector.close()

    return image, result


# %%
# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print("\n🌸 Starting GlowPetals Face Detection...\n")

    print("Image exists:", IMAGE_PATH.exists())
    print("Model exists:", MODEL_PATH.exists())

    output = detect_faces(IMAGE_PATH)

    if output is None:

        print("\n❌ Face detection failed.")

    else:

        image, result = output

        faces = len(result.detections)

        print("\n👤 Faces detected:", faces)

        if faces > 0:

            print("✅ FACE DETECTED SUCCESSFULLY! 🌸")

        else:

            print("❌ No face detected.")
            # %%
import sys
print("Python:", sys.executable)

import cv2
print("OpenCV:", cv2.__version__)

import mediapipe
print("MediaPipe:", mediapipe.__version__)
# %%
