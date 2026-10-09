import sys
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from services.face_analysis import analyze_face
from services.recommendations import get_personalized_recommendations
from werkzeug.exceptions import RequestEntityTooLarge

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 11 * 1024 * 1024

PROJECT_ROOT = Path(__file__).resolve().parent
UPLOAD_FOLDER = PROJECT_ROOT / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({
        "success": False,
        "message": "Image must be 10 MB or smaller.",
    }), 413


@app.route("/")
@app.route("/in")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    print("\n===================================")
    print("GLOWPETALS IMAGE TEST")
    print("===================================")

    try:

        print("/analyze request received")

        image_file = request.files.get("image")
        if image_file is None or not image_file.filename:
            print("IMAGE NOT FOUND IN REQUEST")

            return jsonify({
                "success": False,
                "message": "No image received."
            }), 400

        profile = request.form.get("profile", "female").strip().lower()
        if profile not in {"female", "male", "child"}:
            return jsonify({"success": False, "message": "Choose a valid profile."}), 400
        sensitive_skin = request.form.get("sensitive_skin", "unsure").strip().lower()
        known_ingredients = request.form.get("known_ingredients", "").strip()
        if sensitive_skin not in {"yes", "no", "unsure"}:
            return jsonify({"success": False, "message": "Choose a valid sensitivity option."}), 400
        if len(known_ingredients) > 300:
            return jsonify({
                "success": False,
                "message": "Ingredient notes must be 300 characters or fewer.",
            }), 400
        image_path = UPLOAD_FOLDER / "captured_face.jpg"

        image_file.save(image_path)

        analysis = analyze_face(image_path)

        if not analysis.get("success"):
            return jsonify(analysis), 422

        recommendations = {}
        if analysis.get("face_detected"):
            recommendations = get_personalized_recommendations(
                profile,
                analysis["face_shape"],
                analysis.get("skin_appearance"),
                sensitive_skin=sensitive_skin,
                known_ingredients=known_ingredients,
            )

        print("IMAGE RECEIVED")
        print("SAVED:", image_path)
        print("PROFILE:", profile)
  
        return jsonify({
            "success": True,
            "profile": profile.title(),
            "message": analysis["message"],
            "analysis": analysis,
            "recommendations": recommendations,
            "image_saved": True,
        })

    except RequestEntityTooLarge:
        return jsonify({
            "success": False,
            "message": "Image must be 10 MB or smaller.",
        }), 413
    except OSError as error:
        if getattr(error, "winerror", None) == 4551:
            print("WINDOWS APPLICATION CONTROL BLOCKED THE MEDIAPIPE LIBRARY:", error)
            return jsonify({
                "success": False,
                "message": (
                    "Windows Application Control blocked MediaPipe's required "
                    "native library. Ask your administrator to approve it or "
                    "run the app in an approved Python environment."
                ),
            }), 503
        raise
    except Exception as error:

        print("BACKEND ERROR:", error)

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/recommendations", methods=["POST"])
def recommendations():
    """
    Refresh product recommendations based on updated skincare preferences.
    Does not require a new image upload.
    """
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"success": False, "message": "Request body must be a JSON object."}), 400

        profile = data.get("profile", "female")
        face_shape = data.get("face_shape", "oval")
        skin_appearance = data.get("skin_appearance", {})
        sensitive_skin = str(data.get("sensitive_skin", "unsure")).strip().lower()
        known_ingredients = str(data.get("known_ingredients", "")).strip()

        if sensitive_skin not in {"yes", "no", "unsure"}:
            return jsonify({"success": False, "message": "Choose a valid sensitivity option."}), 400
        if len(known_ingredients) > 300:
            return jsonify({
                "success": False,
                "message": "Ingredient notes must be 300 characters or fewer.",
            }), 400

        recommendations = get_personalized_recommendations(
            profile,
            face_shape,
            skin_appearance,
            sensitive_skin=sensitive_skin,
            known_ingredients=known_ingredients,
        )

        return jsonify({
            "success": True,
            "recommendations": recommendations
        })

    except Exception as error:
        print("RECOMMENDATIONS ENDPOINT ERROR:", error)
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


if __name__ == "__main__":

    print("GlowPetals Flask Server Starting...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )