"""
knowledge_base.py — Built-in product data for popular Indian products.
Used as fallback when Open Food Facts / scraping returns no data.
Covers food, personal care, health, and household products.
"""

PRODUCTS = {
    # ── INSTANT NOODLES ──────────────────────────────────────────────────────
    "maggi": {
        "name": "Maggi 2-Minute Noodles",
        "brand": "Nestle",
        "category": "Food & Beverages / Instant Noodles",
        "description": (
            "Maggi 2-Minute Noodles by Nestle is India's most iconic instant noodle brand, "
            "loved since 1983. Made from wheat flour with a signature masala tastemaker, "
            "it is a quick meal option available in multiple flavours including Masala, "
            "Atta, and Oats variants."
        ),
        "ingredients": "Wheat flour, Palm oil, Salt, Sugar, Maltodextrin, Spices, Tastemaker (Masala)",
        "nutrition": {"calories": 350, "fat": 14, "saturated_fat": 6, "sugar": 2, "sodium": 890, "protein": 8, "fiber": 1.5, "carbs": 50},
        "nutriscore": "d",
        "allergens": ["en:gluten", "en:wheat"],
        "price_range": "₹12–₹65",
        "rating": "4.2 out of 5",
        "reviews": [
            "Great taste, kids love it. Quick and easy to make.",
            "Tastes amazing but not healthy for daily consumption.",
            "The masala flavour is unbeatable. Classic Indian snack.",
            "High in sodium but occasional treat is fine.",
            "Best instant noodles in India, no competition.",
        ],
    },
    "top ramen": {
        "name": "Top Ramen Noodles",
        "brand": "Nissin",
        "category": "Food & Beverages / Instant Noodles",
        "description": (
            "Top Ramen by Nissin is a popular instant noodle brand available in India. "
            "Known for its Smoodles variant with smooth noodles, it comes in flavours "
            "like Masala, Chicken, and Magic Masala."
        ),
        "ingredients": "Wheat flour, Palm oil, Salt, Sugar, Spices, Flavour enhancers",
        "nutrition": {"calories": 340, "fat": 12, "saturated_fat": 5.5, "sugar": 2.5, "sodium": 820, "protein": 7.5, "fiber": 1.2, "carbs": 52},
        "nutriscore": "d",
        "allergens": ["en:gluten", "en:wheat"],
        "price_range": "₹10–₹50",
        "rating": "4.0 out of 5",
        "reviews": [
            "Good alternative to Maggi, slightly less salty.",
            "Smoodles texture is unique and enjoyable.",
            "Not as popular as Maggi but still tasty.",
            "Good value for money.",
        ],
    },
    # ── SOAPS ────────────────────────────────────────────────────────────────
    "santoor": {
        "name": "Santoor Sandal & Turmeric Soap",
        "brand": "Wipro",
        "category": "Beauty & Personal Care / Bathing Soap",
        "description": (
            "Santoor Soap by Wipro is one of India's best-selling bathing soaps. "
            "It contains natural sandalwood and turmeric extracts that help keep "
            "skin soft, smooth, and youthful-looking. Available in multiple variants "
            "including Classic, White, and Aloe Vera."
        ),
        "ingredients": "Sodium Palmate, Sodium Palm Kernelate, Sandalwood Extract, Turmeric Extract, Glycerin, Perfume",
        "nutrition": {},
        "nutriscore": "",
        "allergens": [],
        "price_range": "₹35–₹120",
        "rating": "4.4 out of 5",
        "reviews": [
            "Skin feels soft and fragrant after use. Love the sandalwood smell.",
            "Best soap for daily use. Been using it for years.",
            "Good lather, nice fragrance, affordable price.",
            "Helps with skin glow. The turmeric formula works well.",
            "Classic Indian soap — reliable and effective.",
        ],
    },
    "dettol": {
        "name": "Dettol Original Antibacterial Soap",
        "brand": "Reckitt Benckiser",
        "category": "Beauty & Personal Care / Antibacterial Soap",
        "description": (
            "Dettol Original Soap by Reckitt provides trusted antibacterial protection. "
            "Contains Trichlocarban (TCC) that kills 99.9% of germs. "
            "Ideal for maintaining hygiene and preventing infections."
        ),
        "ingredients": "Sodium Palmate, Sodium Palm Kernelate, Trichlocarban, Glycerin, Perfume, EDTA",
        "nutrition": {},
        "nutriscore": "",
        "allergens": [],
        "price_range": "₹35–₹150",
        "rating": "4.5 out of 5",
        "reviews": [
            "Best antibacterial soap. Feel clean and protected.",
            "The classic dettol smell gives confidence of cleanliness.",
            "Good for family hygiene, especially during flu season.",
            "Slightly drying on skin but excellent germ protection.",
            "Trust factor is very high. Using since childhood.",
        ],
    },
    "dove": {
        "name": "Dove Cream Beauty Bathing Bar",
        "brand": "HUL",
        "category": "Beauty & Personal Care / Moisturising Soap",
        "description": (
            "Dove Beauty Bar by HUL is more than a soap — it contains 1/4 moisturising cream "
            "that helps maintain skin's natural moisture. Dermatologist-recommended and "
            "suitable for sensitive, dry skin."
        ),
        "ingredients": "Sodium Lauroyl Isethionate, Stearic Acid, Sodium Tallowate, Sodium Isethionate, Water, Sodium Stearate, Cocamidopropyl Betaine, Glycerin, Fragrance",
        "nutrition": {},
        "nutriscore": "",
        "allergens": [],
        "price_range": "₹45–₹200",
        "rating": "4.6 out of 5",
        "reviews": [
            "Skin feels incredibly soft after use. Love it.",
            "Best soap for dry skin. The moisturising cream really works.",
            "Gentle on skin, no harsh chemicals. Dermatologist recommended.",
            "Expensive compared to other soaps but worth every rupee.",
            "The only soap that doesn't make my skin feel tight.",
        ],
    },
    # ── SHAMPOOS ─────────────────────────────────────────────────────────────
    "head & shoulders": {
        "name": "Head & Shoulders Anti-Dandruff Shampoo",
        "brand": "P&G",
        "category": "Beauty & Personal Care / Anti-Dandruff Shampoo",
        "description": (
            "Head & Shoulders by P&G is the world's #1 anti-dandruff shampoo. "
            "Contains Zinc Pyrithione that fights dandruff-causing fungus. "
            "Provides up to 100% dandruff protection with regular use."
        ),
        "ingredients": "Water, Sodium Lauryl Sulfate, Sodium Laureth Sulfate, Zinc Pyrithione, Glycol Distearate, Cocamide MEA, Fragrance",
        "nutrition": {},
        "nutriscore": "",
        "allergens": [],
        "price_range": "₹120–₹650",
        "rating": "4.3 out of 5",
        "reviews": [
            "Dandruff gone within 2 weeks of regular use!",
            "Best anti-dandruff shampoo available in India.",
            "Leaves hair feeling clean and fresh.",
            "Slightly drying but works amazingly for dandruff.",
        ],
    },
    "himalaya": {
        "name": "Himalaya Herbals Shampoo",
        "brand": "Himalaya Drug Company",
        "category": "Beauty & Personal Care / Herbal Shampoo",
        "description": (
            "Himalaya Herbals Shampoo contains natural ingredients like Chickpea and Bhringaraj "
            "that nourish hair and prevent hair fall. Free from harsh chemicals, "
            "suitable for daily use. Available in variants for different hair types."
        ),
        "ingredients": "Chickpea (Cicer arietinum), Bhringaraj (Eclipta alba), Aloe Vera, SLES, Water, Preservatives",
        "nutrition": {},
        "nutriscore": "",
        "allergens": [],
        "price_range": "₹90–₹350",
        "rating": "4.2 out of 5",
        "reviews": [
            "Natural ingredients, no harsh chemicals. Safe for daily use.",
            "Reduced hair fall significantly after 4 weeks.",
            "Pleasant herbal fragrance. Leaves hair soft.",
            "Good affordable herbal shampoo. Trustworthy brand.",
        ],
    },
    # ── BISCUITS ─────────────────────────────────────────────────────────────
    "parle-g": {
        "name": "Parle-G Original Glucose Biscuits",
        "brand": "Parle Products",
        "category": "Food & Beverages / Biscuits & Cookies",
        "description": (
            "Parle-G is the world's largest selling biscuit brand and India's most iconic snack. "
            "Made with wheat flour, sugar, and milk solids, it provides quick energy. "
            "The yellow wrapper with the baby girl is instantly recognisable across India."
        ),
        "ingredients": "Wheat Flour, Sugar, Edible Vegetable Oil, Invert Syrup, Milk Solids, Leavening Agents, Salt",
        "nutrition": {"calories": 450, "fat": 10, "saturated_fat": 4.5, "sugar": 22, "sodium": 350, "protein": 7, "fiber": 1, "carbs": 76},
        "nutriscore": "d",
        "allergens": ["en:gluten", "en:wheat", "en:milk"],
        "price_range": "₹5–₹50",
        "rating": "4.5 out of 5",
        "reviews": [
            "Childhood favourite! Taste hasn't changed in decades.",
            "Best value biscuit. Great with chai.",
            "High in sugar but loved by everyone.",
            "Crispy, mildly sweet — perfect tea-time biscuit.",
        ],
    },
    # ── FACE CARE ────────────────────────────────────────────────────────────
    "himalaya face wash": {
        "name": "Himalaya Purifying Neem Face Wash",
        "brand": "Himalaya Drug Company",
        "category": "Beauty & Personal Care / Face Wash",
        "description": (
            "Himalaya Purifying Neem Face Wash contains Neem and Turmeric extracts that "
            "gently cleanse the skin, remove excess oil, and prevent pimples and acne. "
            "Soap-free formula suitable for oily and combination skin."
        ),
        "ingredients": "Neem (Azadirachta indica) Leaf Extract, Turmeric (Curcuma longa) Rhizome Extract, Cocamidopropyl Betaine, Water, Glycerin",
        "nutrition": {},
        "nutriscore": "",
        "allergens": [],
        "price_range": "₹75–₹300",
        "rating": "4.3 out of 5",
        "reviews": [
            "Cleared my acne in 3 weeks! Highly recommend.",
            "Gentle on skin, doesn't over-dry. Perfect for daily use.",
            "Neem fragrance is strong but effective.",
            "Best face wash for oily skin in this price range.",
        ],
    },
    # ── COOKING OIL ──────────────────────────────────────────────────────────
    "fortune": {
        "name": "Fortune Refined Sunflower Oil",
        "brand": "Adani Wilmar",
        "category": "Food & Beverages / Cooking Oil",
        "description": (
            "Fortune Sunflower Oil by Adani Wilmar is light, healthy cooking oil "
            "rich in Vitamin E and low in saturated fat. Ideal for frying, sautéing, "
            "and everyday Indian cooking. India's most trusted cooking oil brand."
        ),
        "ingredients": "100% Refined Sunflower Oil",
        "nutrition": {"calories": 900, "fat": 100, "saturated_fat": 11, "sugar": 0, "sodium": 0, "protein": 0, "fiber": 0, "carbs": 0},
        "nutriscore": "",
        "allergens": [],
        "price_range": "₹140–₹600",
        "rating": "4.3 out of 5",
        "reviews": [
            "Light oil, food doesn't feel greasy. Love it.",
            "Best sunflower oil. Good for heart health.",
            "Clean taste, no strong smell. Perfect for Indian cooking.",
        ],
    },
    # ── DAIRY ────────────────────────────────────────────────────────────────
    "amul butter": {
        "name": "Amul Butter",
        "brand": "AMUL",
        "category": "Food & Beverages / Dairy",
        "description": (
            "Amul Butter is India's most loved butter, made from fresh cream. "
            "Rich, creamy taste perfect for spreading on bread, cooking, and baking. "
            "The iconic red and white packaging is a staple in every Indian household."
        ),
        "ingredients": "Butter (from Pasteurised Cream), Common Salt",
        "nutrition": {"calories": 720, "fat": 81, "saturated_fat": 50, "sugar": 0.5, "sodium": 650, "protein": 0.5, "fiber": 0, "carbs": 0.5},
        "nutriscore": "e",
        "allergens": ["en:milk"],
        "price_range": "₹55–₹500",
        "rating": "4.6 out of 5",
        "reviews": [
            "The taste of Amul butter is unmatched. Utterly Butterly Delicious!",
            "Best butter in India. Consistent quality always.",
            "Goes with everything — paratha, bread, dal. Love it.",
        ],
    },
}


def lookup(product_name: str) -> dict | None:
    """
    Return built-in product data if the name matches any entry.
    Case-insensitive, partial match supported.
    """
    name_lower = product_name.lower().strip()
    # Exact / startswith match first
    for key, data in PRODUCTS.items():
        if key in name_lower or name_lower in key:
            return _to_product_data(data)
    return None


def _to_product_data(data: dict) -> dict:
    """Convert knowledge base entry to standard product_data format."""
    return {
        "name": data["name"],
        "brand": data["brand"],
        "category": data["category"],
        "description": data["description"],
        "ingredients": data.get("ingredients", ""),
        "image_url": "",
        "quantity": "",
        "labels": "",
        "nutriscore": data.get("nutriscore", ""),
        "allergens": data.get("allergens", []),
        "nutrition": data.get("nutrition", {}),
        "price_range": data.get("price_range", ""),
        "kb_rating": data.get("rating", ""),
        "kb_reviews": data.get("reviews", []),
        "source": "knowledge_base",
    }
