# ============================================================
# GLOWPETALS - PROFILE SELECTION
# ============================================================

def select_profile():

    print("\n" + "=" * 50)
    print("🌸 GLOWPETALS PROFILE")
    print("=" * 50)

    print("\nChoose your profile:")

    print("1️⃣ Female")
    print("2️⃣ Male")
    print("3️⃣ Child")

    choice = input("\nEnter 1, 2, or 3: ").strip()

    profiles = {
        "1": "Female",
        "2": "Male",
        "3": "Child"
    }

    if choice in profiles:

        selected_profile = profiles[choice]

        print(
            f"\n✅ Selected Profile: {selected_profile}"
        )

        return selected_profile

    else:

        print("\n❌ Invalid choice.")
        print("Please select 1, 2, or 3.")

        return None


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    profile = select_profile()

    if profile:

        print(
            f"🌸 GlowPetals will use the {profile} "
            "recommendation section."
        )