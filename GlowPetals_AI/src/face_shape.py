# ============================================================
# GLOWPETALS - FACE SHAPE ANALYSIS MODULE
# ============================================================

import math


# ============================================================
# DISTANCE FUNCTION
# ============================================================

def distance(point1, point2):

    return math.sqrt(
        (point1.x - point2.x) ** 2 +
        (point1.y - point2.y) ** 2
    )


# ============================================================
# FACE SHAPE ANALYSIS
# ============================================================

def analyze_face_shape(landmarks):

    forehead_left = landmarks[54]
    forehead_right = landmarks[284]

    cheek_left = landmarks[234]
    cheek_right = landmarks[454]

    jaw_left = landmarks[172]
    jaw_right = landmarks[397]

    top = landmarks[10]
    bottom = landmarks[152]

    # Measurements
    face_length = distance(top, bottom)

    forehead_width = distance(
        forehead_left,
        forehead_right
    )

    cheekbone_width = distance(
        cheek_left,
        cheek_right
    )

    jaw_width = distance(
        jaw_left,
        jaw_right
    )

    # Ratios
    width_length_ratio = (
        cheekbone_width / face_length
    )

    jaw_cheek_ratio = (
        jaw_width / cheekbone_width
    )

    forehead_cheek_ratio = (
        forehead_width / cheekbone_width
    )

    # Face shape classification
    if width_length_ratio < 0.72:

        face_shape = "Oblong"

    elif width_length_ratio > 0.88:

        if jaw_cheek_ratio > 0.85:
            face_shape = "Square"
        else:
            face_shape = "Round"

    elif jaw_cheek_ratio < 0.72:

        face_shape = "Heart"

    elif forehead_cheek_ratio < 0.78:

        face_shape = "Diamond"

    else:

        face_shape = "Oval"

    return {
        "face_shape": face_shape,
        "face_length": face_length,
        "forehead_width": forehead_width,
        "cheekbone_width": cheekbone_width,
        "jaw_width": jaw_width,
        "width_length_ratio": width_length_ratio,
        "jaw_cheek_ratio": jaw_cheek_ratio,
        "forehead_cheek_ratio": forehead_cheek_ratio
    }