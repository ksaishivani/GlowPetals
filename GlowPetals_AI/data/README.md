# Skincare product catalog

`skincare_products.csv` is the local product catalog used after a successful face scan. The face scan contributes only a low-confidence visible-shine estimate; product filtering uses the user's self-reported skin type and sensitivity.

## Fields

- `brand`, `name`, `type`: product-card text.
- `image`, `url`: product image and product page.
- `why`: short, non-medical explanation displayed with the product.
- `skin_types`: semicolon-separated values from `oily`, `dry`, `combination`, and `normal`.
- `sensitive_suitable`: set to `true` only when the catalog has a basis for showing the product to someone who reports sensitive skin.
- `child_suitable`: set to `true` only after age-specific suitability is verified; current entries are not marked for children.
- `ingredients_verified`, `ingredients`: mark complete, current ingredient data as verified and list exact ingredient names separated by semicolons. Allergy filtering uses exact names and only considers rows marked verified.

Keep product claims, image URLs, and ingredient data aligned with the current product packaging and brand listing. If a user reports an allergy but no complete ingredient lists are verified, the app deliberately withholds product recommendations.
