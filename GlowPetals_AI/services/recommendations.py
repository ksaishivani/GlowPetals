import csv
import re
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data"
PROFILE_FILES = {
    "female": "female_recommendations.csv",
    "male": "male_recommendations.csv",
    "child": "child_recommendations.csv",
}

SENSITIVITY_OPTIONS = {"yes", "no", "unsure"}
SKINCARE_CATALOG_PATH = DATA_PATH / "skincare_products.csv"
MAKEUP_CATALOG_PATH = DATA_PATH / "makeup_products.csv"


def _skin_types_from_analysis(skin_appearance):
    if not isinstance(skin_appearance, dict):
        return set(), "Unavailable"

    try:
        shine_percent = float(skin_appearance["visible_shine_percent"])
    except (KeyError, TypeError, ValueError):
        return set(), "Unavailable"

    if not 0 <= shine_percent <= 100:
        return set(), "Unavailable"
    if shine_percent >= 12:
        return {"oily"}, "Oily-leaning visible shine"
    if shine_percent >= 4.5:
        return {"combination"}, "Combination-leaning visible shine"
    return {"normal"}, "Balanced/low-shine appearance"


def _limit_product_variety(products, limit):
    selected = []
    type_counts = {}
    for product in products:
        product_type = product["type"]
        if type_counts.get(product_type, 0) >= 2:
            continue
        selected.append(product)
        type_counts[product_type] = type_counts.get(product_type, 0) + 1
        if len(selected) == limit:
            break
    return selected


def _get_skin_products(matched_skin_types, sensitive_skin, known_ingredients, profile):
    with SKINCARE_CATALOG_PATH.open(encoding="utf-8-sig", newline="") as csv_file:
        catalog = list(csv.DictReader(csv_file))

    if profile == "child":
        catalog = [
            product for product in catalog
            if product["child_suitable"].strip().lower() == "true"
        ]
        if not catalog:
            return [], (
                "This catalog is not verified for children. Ask a parent or guardian "
                "and a pediatric clinician to choose products."
            )

    allergy_terms = {
        term.strip().lower()
        for term in re.split(r"[,;]", known_ingredients)
        if term.strip()
    }
    if allergy_terms:
        catalog = [
            product for product in catalog
            if product["ingredients_verified"].strip().lower() == "true"
            and product["ingredients"].strip()
        ]
        if not catalog:
            return [], (
                "No products were recommended because the catalog does not yet have "
                "complete verified ingredient lists for allergy screening. Check each "
                "product's full ingredient label with a qualified professional."
            )

    if not matched_skin_types:
        return [], (
            "A clear face scan is needed to create a product shortlist. The scan "
            "estimates visible shine only and cannot diagnose skin type."
        )

    products = []
    for product in catalog:
        product_skin_types = {
            item.strip().lower()
            for item in product["skin_types"].split(";")
        }
        if not matched_skin_types.intersection(product_skin_types):
            continue
        if (
            sensitive_skin == "yes"
            and product["sensitive_suitable"].strip().lower() != "true"
        ):
            continue
        product_ingredients = {
            item.strip().lower()
            for item in product["ingredients"].split(";")
        }
        if allergy_terms & product_ingredients:
            continue
        products.append({
            key: product[key]
            for key in ("brand", "name", "type", "image", "url", "why")
        })

    if not products:
        return [], (
            "No catalog products matched the scan and safety filters. Review "
            "product labels or consult a qualified skincare professional."
        )
    if allergy_terms:
        note = (
            "Products were filtered against exact ingredient names in the verified "
            "catalog. Confirm the current packaging because formulas can change."
        )
    elif sensitive_skin == "yes":
        note = (
            "Shortlisted using the scan's low-confidence visible-shine estimate "
            "and products flagged for sensitive-skin positioning. Patch-test and "
            "review labels."
        )
    else:
        note = (
            "Shortlisted by the scan's low-confidence visible-shine estimate, not "
            "a diagnosis of skin type. Lighting and makeup can affect the result."
        )
    return _limit_product_variety(products, 3), note


def _get_makeup_products(matched_skin_types, skin_tone, profile):
    """Load makeup products matching the available face-analysis signals."""
    if not MAKEUP_CATALOG_PATH.exists():
        return []

    with MAKEUP_CATALOG_PATH.open(encoding="utf-8-sig", newline="") as csv_file:
        catalog = list(csv.DictReader(csv_file))

    if profile == "child":
        catalog = [
            product for product in catalog
            if product.get("age_verified", "false").strip().lower() == "true"
        ]

    if not matched_skin_types:
        return []

    products = []
    for product in catalog:
        product_skin_types = {
            item.strip().lower()
            for item in product.get("skin_types", "").split(";")
            if item.strip()
        }
        if not matched_skin_types.intersection(product_skin_types):
            continue

        product_skin_tones = {
            item.strip().lower()
            for item in product.get("skin_tones", "").split(";")
            if item.strip()
        }
        if skin_tone and skin_tone.lower() not in product_skin_tones:
            continue

        products.append({
            key: product[key]
            for key in ("brand", "name", "type", "image", "url", "why")
        })

    return _limit_product_variety(products, 6)



def _braid_ideas(face_shape):
    shape = str(face_shape).strip().lower()
    framing = {
        "round": "with a side part to add visual length",
        "oblong": "with soft side volume and a low crown",
        "square": "with loose face-framing pieces",
        "heart": "with a soft side-swept front",
        "diamond": "with cheek-level face-framing pieces",
        "oval": "with a balanced center or side part",
    }.get(shape, "with a comfortable face-framing part")
    return {
        "Everyday": [
            f"Loose side braid {framing}",
            "Simple three-strand braid",
            "Low braided ponytail",
        ],
        "Wedding": [
            f"Soft Dutch crown braid {framing}",
            "Fishtail braided low bun with a veil or floral pins",
            "Romantic French braid into a chignon",
        ],
        "Party": [
            f"Textured fishtail side braid {framing}",
            "Braided half-up waves",
            "Double Dutch braids into a high ponytail",
        ],
        "Formal": [
            "Sleek French braid into a low bun",
            f"Polished braided chignon {framing}",
            "Single Dutch braid tucked into a neat low updo",
        ],
        "Festival": [
            f"Boho crown braid {framing}",
            "Double Dutch braids with soft ribbons",
            "Loose fishtail braid with small hair accessories",
        ],
    }


def get_personalized_recommendations(
    profile,
    face_shape,
    skin_appearance=None,
    sensitive_skin="unsure",
    known_ingredients="",
):
    profile_key = str(profile).strip().lower()
    shape_key = str(face_shape).strip().lower()
    sensitive_skin = str(sensitive_skin).strip().lower()
    known_ingredients = str(known_ingredients).strip()

    if sensitive_skin not in SENSITIVITY_OPTIONS:
        sensitive_skin = "unsure"

    filename = PROFILE_FILES.get(profile_key)
    matches = {}

    if filename and shape_key:
        with (DATA_PATH / filename).open(encoding="utf-8-sig", newline="") as csv_file:
            for row in csv.DictReader(csv_file):
                if row.get("face_shape", "").strip().lower() != shape_key:
                    continue
                category = row.get("category", "Style").strip()
                recommendation = row.get("recommendation", "").strip()
                if recommendation:
                    matches.setdefault(category, []).append(recommendation)

    skin_label = ""
    if isinstance(skin_appearance, dict):
        skin_label = str(skin_appearance.get("label", ""))
    matched_skin_types, skin_match_label = _skin_types_from_analysis(skin_appearance)
    skin_products, skincare_note = _get_skin_products(
        matched_skin_types, sensitive_skin, known_ingredients, profile_key
    )
    skin_tone = skin_appearance.get("skin_tone", "") if isinstance(skin_appearance, dict) else ""
    makeup_products = _get_makeup_products(matched_skin_types, skin_tone, profile_key)

    return {
        "face_shape_matches": matches,
        "skin_appearance": skin_label,
        "skin_match_label": skin_match_label,
        "skin_product_guidance": skin_products,
        "skin_product_note": skincare_note,
        "makeup_product_guidance": makeup_products,
        "occasion_braids": _braid_ideas(face_shape),
        "product_catalog_note": "The local catalog is a starting point, not medical advice. Confirm current ingredients, product variant, age suitability, and directions; patch-test new skincare products.",
    }