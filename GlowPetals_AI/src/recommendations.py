# ============================================================
# GLOWPETALS - RECOMMENDATION ENGINE
# ============================================================

import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    r"C:\Users\HP\Desktop\GlowPetals_AI"
)

DATA_PATH = PROJECT_ROOT / "data"


# ============================================================
# LOAD DATASET
# ============================================================

def load_recommendation_data(profile):

    profile_map = {
        "1": "female_recommendations.csv",
        "2": "male_recommendations.csv",
        "3": "child_recommendations.csv",
        "female": "female_recommendations.csv",
        "male": "male_recommendations.csv",
        "child": "child_recommendations.csv"
    }

    # Remove spaces and make lowercase
    profile_key = str(profile).strip().lower()

    if profile_key not in profile_map:

        print("❌ Invalid profile.")
        print("Please enter:")
        print("1 = Female")
        print("2 = Male")
        print("3 = Child")

        return None

    file_path = DATA_PATH / profile_map[profile_key]

    if not file_path.exists():

        print("❌ Dataset not found:")
        print(file_path)

        return None

    df = pd.read_csv(file_path)

    print("✅ Recommendation dataset loaded!")
    print("📁 File:", file_path.name)
    print("📊 Dataset rows:", len(df))

    return df


# ============================================================
# GET RECOMMENDATIONS
# ============================================================

def get_recommendations(profile, face_shape):

    df = load_recommendation_data(profile)

    if df is None:
        return None

    shape = str(face_shape).strip().lower()

    filtered = df[
        df["face_shape"]
        .astype(str)
        .str.strip()
        .str.lower()
        == shape
    ]

    if filtered.empty:

        print(
            f"❌ No recommendations found for {face_shape}."
        )

        return None

    return filtered


# ============================================================
# DISPLAY RECOMMENDATIONS
# ============================================================

def display_recommendations(profile, face_shape):

    recommendations = get_recommendations(
        profile,
        face_shape
    )

    if recommendations is None:
        return

    print("\n" + "=" * 60)
    print("🌸 GLOWPETALS PERSONALIZED RECOMMENDATIONS")
    print("=" * 60)

    print("👤 Profile:", profile)
    print("✨ Face Shape:", face_shape)

    print("=" * 60)

    # Display each category
    for category in recommendations["category"].unique():

        print(f"\n💡 {category}")

        category_data = recommendations[
            recommendations["category"] == category
        ]

        for recommendation in category_data[
            "recommendation"
        ].tolist():

            print("   •", recommendation)

    print("\n" + "=" * 60)
    print("✅ Recommendations generated successfully!")
    print("=" * 60)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n🌸 GLOWPETALS RECOMMENDATION ENGINE")
    print("=" * 60)

    print("\nChoose profile:")
    print("1️⃣ Female")
    print("2️⃣ Male")
    print("3️⃣ Child")

    profile = input(
        "\nEnter 1, 2, or 3: "
    )

    print("\nAvailable face shapes:")
    print("Oval")
    print("Round")
    print("Square")
    print("Heart")
    print("Diamond")
    print("Oblong")

    face_shape = input(
        "\nEnter face shape: "
    )

    display_recommendations(
        profile,
        face_shape
    )