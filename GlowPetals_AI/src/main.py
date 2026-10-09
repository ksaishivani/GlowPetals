# ============================================================
# 🌸 GLOWPETALS AI - COMPLETE PIPELINE
# ============================================================

from pathlib import Path

from landmarks import detect_landmarks
from face_shape import analyze_face_shape
from recommendations import display_recommendations


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    r"C:\Users\HP\Desktop\GlowPetals_AI"
)

IMAGE_PATH = (
    PROJECT_ROOT
    / "assets"
    / "test_face.jpg"
)


# ============================================================
# START
# ============================================================

print("\n" + "=" * 60)
print("🌸 GLOWPETALS AI - COMPLETE ANALYSIS")
print("=" * 60)


# ============================================================
# CHECK IMAGE
# ============================================================

print("\n📷 Checking image...")

if not IMAGE_PATH.exists():

    print("❌ Image not found!")
    print("Path:", IMAGE_PATH)

    raise SystemExit

print("✅ Image exists!")


# ============================================================
# STEP 1 — FACIAL LANDMARKS
# ============================================================

print("\n" + "-" * 60)
print("📍 STEP 1: FACIAL LANDMARK DETECTION")
print("-" * 60)

result = detect_landmarks(
    IMAGE_PATH
)

if result is None:

    print("❌ Facial landmark detection failed.")

    raise SystemExit


image, landmarks = result

print("\n🎉 Landmark detection successful!")
print("📍 Total landmarks:", len(landmarks))


# ============================================================
# STEP 2 — FACE SHAPE
# ============================================================

print("\n" + "-" * 60)
print("📐 STEP 2: FACE SHAPE ANALYSIS")
print("-" * 60)

analysis = analyze_face_shape(
    landmarks
)

face_shape = analysis["face_shape"]

print(
    "\n✨ Detected Face Shape:",
    face_shape
)

print(
    "📏 Face Length:",
    round(
        analysis["face_length"],
        4
    )
)

print(
    "📐 Cheekbone Width:",
    round(
        analysis["cheekbone_width"],
        4
    )
)

print(
    "📊 Width/Length Ratio:",
    round(
        analysis["width_length_ratio"],
        4
    )
)


# ============================================================
# STEP 3 — PROFILE
# ============================================================

print("\n" + "-" * 60)
print("👤 STEP 3: PROFILE SELECTION")
print("-" * 60)

print("\nChoose profile:")

print("1️⃣ Female")
print("2️⃣ Male")
print("3️⃣ Child")

profile_choice = input(
    "\nEnter 1, 2, or 3: "
).strip()


profile_map = {
    "1": "Female",
    "2": "Male",
    "3": "Child"
}


if profile_choice not in profile_map:

    print("\n❌ Invalid profile.")

    raise SystemExit


profile = profile_map[
    profile_choice
]

print(
    "\n✅ Selected Profile:",
    profile
)


# ============================================================
# STEP 4 — RECOMMENDATIONS
# ============================================================

print("\n" + "-" * 60)
print("🧠 STEP 4: PERSONALIZED RECOMMENDATIONS")
print("-" * 60)

display_recommendations(
    profile,
    face_shape
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("🌸 GLOWPETALS ANALYSIS COMPLETED!")
print("=" * 60)