"""
analyser.py — Rule-based analysis engine.
Converts raw product data into structured pros/cons, health warnings,
sentiment scores, usage guidance, alternatives, and an overall verdict.
"""

import re


# ---------------------------------------------------------------------------
# Sentiment analysis (VADER)
# ---------------------------------------------------------------------------

def analyse_sentiment(reviews: list[str]) -> dict:
    """Run VADER sentiment over a list of review strings."""
    if not reviews:
        return {"positive": 0, "negative": 0, "neutral": 100,
                "overall": "No Reviews", "score": 5.0}
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        totals = {"pos": 0.0, "neg": 0.0, "neu": 0.0}
        for r in reviews:
            s = sia.polarity_scores(r)
            totals["pos"] += s["pos"]
            totals["neg"] += s["neg"]
            totals["neu"] += s["neu"]
        n = len(reviews)
        pos = round(totals["pos"] / n * 100)
        neg = round(totals["neg"] / n * 100)
        neu = 100 - pos - neg

        if pos >= 50:
            overall = "Positive"
        elif neg >= 35:
            overall = "Negative"
        else:
            overall = "Mixed"

        # Map to 0-10 scale
        score = round(max(0.0, min(10.0, (pos - neg + 100) / 20)), 1)
        return {"positive": pos, "negative": neg, "neutral": max(0, neu),
                "overall": overall, "score": score}
    except ImportError:
        # VADER not installed — estimate from keyword counting
        return _fallback_sentiment(reviews)


def _fallback_sentiment(reviews: list[str]) -> dict:
    pos_words = {"good", "great", "excellent", "love", "amazing", "best",
                 "recommend", "happy", "nice", "perfect", "fantastic", "awesome"}
    neg_words = {"bad", "poor", "terrible", "hate", "worst", "awful",
                 "disappointed", "waste", "broken", "defective", "horrible"}
    pos_count = neg_count = 0
    for r in reviews:
        words = set(r.lower().split())
        pos_count += len(words & pos_words)
        neg_count += len(words & neg_words)
    total = pos_count + neg_count or 1
    pos_pct = round(pos_count / total * 100)
    neg_pct = round(neg_count / total * 100)
    neu_pct = 100 - pos_pct - neg_pct
    overall = "Positive" if pos_pct > 50 else ("Negative" if neg_pct > 35 else "Mixed")
    score = round(max(0.0, min(10.0, (pos_pct - neg_pct + 100) / 20)), 1)
    return {"positive": pos_pct, "negative": neg_pct, "neutral": max(0, neu_pct),
            "overall": overall, "score": score}


# ---------------------------------------------------------------------------
# Nutrition rule engine
# ---------------------------------------------------------------------------

def analyse_nutrition(nutrition: dict) -> tuple[list, list, list]:
    """Return (warnings, pros, cons) lists based on nutrition thresholds."""
    warnings, pros, cons = [], [], []

    calories = float(nutrition.get("calories") or 0)
    fat = float(nutrition.get("fat") or 0)
    sat_fat = float(nutrition.get("saturated_fat") or 0)
    sugar = float(nutrition.get("sugar") or 0)
    sodium = float(nutrition.get("sodium") or 0)   # mg per 100g
    protein = float(nutrition.get("protein") or 0)
    fiber = float(nutrition.get("fiber") or 0)

    # ---- Sodium ----
    if sodium > 600:
        cons.append(f"High sodium ({sodium:.0f} mg / 100 g)")
        warnings.append("Avoid if you have hypertension or heart disease")
    elif sodium < 200 and sodium > 0:
        pros.append("Low sodium — heart-friendly")

    # ---- Sugar ----
    if sugar > 20:
        cons.append(f"High sugar content ({sugar:.1f} g / 100 g)")
        warnings.append("Not suitable for diabetics or blood-sugar management")
    elif 0 < sugar < 5:
        pros.append("Low sugar — suitable for diabetics")

    # ---- Calories ----
    if calories > 400:
        cons.append(f"High calorie ({calories:.0f} kcal / 100 g)")
        warnings.append("Consume in moderation if managing weight")
    elif 0 < calories < 100:
        pros.append(f"Low calorie ({calories:.0f} kcal) — good for weight management")

    # ---- Fat ----
    if fat > 20:
        cons.append(f"High total fat ({fat:.1f} g / 100 g)")
    elif 0 < fat < 3:
        pros.append("Very low fat content")

    if sat_fat > 10:
        warnings.append(f"High saturated fat ({sat_fat:.1f} g) — increases cholesterol risk")

    # ---- Protein ----
    if protein > 10:
        pros.append(f"Good protein source ({protein:.1f} g / 100 g)")

    # ---- Fiber ----
    if fiber > 5:
        pros.append(f"High dietary fiber ({fiber:.1f} g) — supports digestion")

    return warnings, pros, cons


# ---------------------------------------------------------------------------
# Score calculation
# ---------------------------------------------------------------------------

def calculate_score(nutrition: dict, sentiment_score: float, rating_str: str) -> float:
    """Return an overall 0–10 score combining nutrition, sentiment, and rating."""
    score = 5.0

    # Sentiment contribution (±1.5)
    score += (sentiment_score - 5) * 0.3

    # Star rating contribution
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:out of|/)\s*5", str(rating_str), re.I)
    if not m:
        m = re.search(r"(\d+(?:\.\d+)?)", str(rating_str))
    if m:
        rating = float(m.group(1))
        if rating <= 5:
            score += (rating - 3) * 0.5   # ±1.0

    # Nutrition penalties
    n_warnings, _, _ = analyse_nutrition(nutrition)
    score -= len(n_warnings) * 0.4

    return round(max(0.0, min(10.0, score)), 1)


# ---------------------------------------------------------------------------
# Pros / cons generator
# ---------------------------------------------------------------------------

_GENERIC_PROS = [
    "Widely available in stores and online",
    "Established brand with proven track record",
    "Suitable for everyday use",
    "Good value for money",
    "Easy to use — no special preparation needed",
    "Consistent quality across batches",
]

_GENERIC_CONS = [
    "May contain preservatives — check label",
    "Packaging may not be eco-friendly",
    "Individual results or taste may vary",
    "Not ideal for all age groups without guidance",
]


def generate_pros_cons(product_data: dict) -> tuple[list, list]:
    """Build a final list of 5 pros and 4 cons from all available signals."""
    pros, cons = [], []

    _, n_pros, n_cons = analyse_nutrition(product_data.get("nutrition", {}))
    pros.extend(n_pros)
    cons.extend(n_cons)

    name = (product_data.get("name") or "").lower()
    labels = (product_data.get("labels") or "").lower()
    nutriscore = (product_data.get("nutriscore") or "").lower()
    ingredients = (product_data.get("ingredients") or "").lower()

    if "organic" in name or "organic" in labels:
        pros.append("Certified organic — no synthetic pesticides or fertilisers")
    if "sugar free" in name or "zero sugar" in name:
        pros.append("Sugar-free formulation")
    if "gluten free" in name or "gluten-free" in labels:
        pros.append("Gluten-free — safe for coeliac patients")
    if "vegan" in labels or "plant based" in name:
        pros.append("Vegan / plant-based friendly")

    if nutriscore in ("a", "b"):
        pros.append(f"Good Nutri-Score ({nutriscore.upper()}) — balanced nutritional profile")
    elif nutriscore in ("d", "e"):
        cons.append(f"Poor Nutri-Score ({nutriscore.upper()}) — limited nutritional value")

    if "artificial" in ingredients:
        cons.append("Contains artificial additives or colours")
    if "palm oil" in ingredients:
        cons.append("Contains palm oil — environmental concern for some consumers")

    # Pad to minimum counts
    for p in _GENERIC_PROS:
        if len(pros) >= 5:
            break
        if p not in pros:
            pros.append(p)

    for c in _GENERIC_CONS:
        if len(cons) >= 4:
            break
        if c not in cons:
            cons.append(c)

    return pros[:5], cons[:4]


# ---------------------------------------------------------------------------
# Health warnings
# ---------------------------------------------------------------------------

def generate_health_warnings(product_data: dict) -> list[str]:
    """Aggregate all health and allergen warnings for the product."""
    warnings = []

    n_warnings, _, _ = analyse_nutrition(product_data.get("nutrition", {}))
    warnings.extend(n_warnings)

    allergens = product_data.get("allergens") or []
    if isinstance(allergens, str):
        allergens = [a.strip() for a in allergens.replace("en:", "").split(",") if a.strip()]
    for allergen in allergens[:4]:
        clean = allergen.replace("en:", "").strip().title()
        if clean:
            warnings.append(f"Contains allergen: {clean}")

    ingredients = (product_data.get("ingredients") or "").lower()
    if "artificial" in ingredients:
        warnings.append("Contains artificial additives — may not suit sensitive individuals")
    if "preservative" in ingredients:
        warnings.append("Contains preservatives — consume within shelf life")

    if not warnings:
        warnings.append("No major health warnings identified for this product")

    return warnings


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def get_verdict(score: float) -> tuple[str, str, str]:
    """Return (label, explanation, colour) based on overall score."""
    if score >= 7.5:
        return (
            "✅ Recommended",
            "Great product overall. Well-suited for regular use. Go ahead and buy it.",
            "green",
        )
    elif score >= 6.0:
        return (
            "👍 Good Choice",
            "Solid product with minor drawbacks. Suitable for most users.",
            "blue",
        )
    elif score >= 4.5:
        return (
            "⚠️ Use with Caution",
            "Average product. Review the warnings and check if it fits your needs.",
            "orange",
        )
    else:
        return (
            "❌ Not Recommended",
            "Several significant concerns. Consider one of the listed alternatives instead.",
            "red",
        )


# ---------------------------------------------------------------------------
# Usage info
# ---------------------------------------------------------------------------

_USAGE_MAP = {
    ("food", "beverage", "snack", "grocery", "dairy", "cereal", "drink", "juice"): {
        "instructions": [
            "Follow serving size printed on the package",
            "Check expiry date before consuming",
            "Store opened packs in an airtight container",
        ],
        "frequency": "As per dietary requirements",
        "best_time": "Any time of day",
        "storage": "Cool, dry place — refrigerate after opening if instructed",
    },
    ("beauty", "cosmetic", "skin", "hair", "cream", "lotion", "shampoo", "face", "soap", "body wash", "cleanser"): {
        "instructions": [
            "Cleanse skin / hair before application",
            "Perform a patch test 24 h before first use",
            "Apply as directed on the label",
        ],
        "frequency": "As directed on product label",
        "best_time": "Morning and / or evening routine",
        "storage": "Store below 30 °C, away from direct sunlight",
    },
    ("medicine", "supplement", "tablet", "capsule", "syrup", "vitamin"): {
        "instructions": [
            "Follow prescribed or label-recommended dosage only",
            "Consult a doctor before use if pregnant or on medication",
            "Do not exceed recommended daily intake",
        ],
        "frequency": "As prescribed or directed",
        "best_time": "As specified on label (with / without food)",
        "storage": "Store in a cool, dry place away from children",
    },
    ("electronic", "gadget", "device", "appliance"): {
        "instructions": [
            "Read the user manual before first use",
            "Ensure correct voltage / power supply",
            "Keep away from moisture and extreme heat",
        ],
        "frequency": "As needed",
        "best_time": "N/A",
        "storage": "Store in a dry environment; original packaging if possible",
    },
}

_DEFAULT_USAGE = {
    "instructions": [
        "Read the product label for specific instructions",
        "Follow manufacturer guidelines",
        "Consult a professional if unsure about suitability",
    ],
    "frequency": "As required or directed",
    "best_time": "As per product instructions",
    "storage": "Store as indicated on packaging",
}


def get_usage_info(product_data: dict) -> dict:
    category = (product_data.get("category") or "").lower()
    name = (product_data.get("name") or "").lower()
    combined = category + " " + name
    for keywords, info in _USAGE_MAP.items():
        if any(k in combined for k in keywords):
            return info
    return _DEFAULT_USAGE


# ---------------------------------------------------------------------------
# Target audience
# ---------------------------------------------------------------------------

def get_target_audience(product_data: dict) -> list[str]:
    name = (product_data.get("name") or "").lower()
    category = (product_data.get("category") or "").lower()
    nutrition = product_data.get("nutrition", {})
    labels = (product_data.get("labels") or "").lower()

    audiences = []

    if float(nutrition.get("protein") or 0) > 15:
        audiences.append("Athletes and fitness enthusiasts")
    if float(nutrition.get("sugar") or 0) < 5:
        audiences.append("Diabetics and sugar-conscious individuals")
    if "baby" in name or "infant" in category:
        audiences.append("Infants / toddlers (consult paediatrician)")
    if "senior" in name or "elder" in name:
        audiences.append("Senior citizens")
    if "organic" in labels or "natural" in name:
        audiences.append("Health-conscious consumers preferring natural products")
    if "vegan" in labels:
        audiences.append("Vegan and plant-based lifestyle followers")

    if not audiences:
        audiences = ["General adults (18+)", "Families and households"]

    return audiences[:4]


# ---------------------------------------------------------------------------
# Alternatives
# ---------------------------------------------------------------------------

_ALTERNATIVES_DB = {
    "noodle": [
        {"name": "Yippee Noodles", "brand": "Sunfeast", "difference": "Lower sodium variant", "price": "₹15–20"},
        {"name": "Top Ramen", "brand": "Nissin", "difference": "Different flavour range", "price": "₹15–25"},
        {"name": "Knorr Soupy Noodles", "brand": "HUL", "difference": "Soupy variant", "price": "₹20–30"},
    ],
    "soap": [
        {"name": "Dove Soap", "brand": "HUL", "difference": "Moisturising formula", "price": "₹45–65"},
        {"name": "Pears Soap", "brand": "HUL", "difference": "Glycerin-based, gentle", "price": "₹45–60"},
        {"name": "Lifebuoy Soap", "brand": "HUL", "difference": "Antibacterial focus", "price": "₹30–50"},
    ],
    "shampoo": [
        {"name": "Dove Shampoo", "brand": "HUL", "difference": "Moisture-focused", "price": "₹160–270"},
        {"name": "Pantene Shampoo", "brand": "P&G", "difference": "Protein-enriched", "price": "₹150–260"},
        {"name": "Himalaya Shampoo", "brand": "Himalaya", "difference": "Herbal formula", "price": "₹100–200"},
    ],
    "biscuit": [
        {"name": "Parle-G", "brand": "Parle", "difference": "Classic glucose biscuit", "price": "₹5–30"},
        {"name": "Good Day", "brand": "Britannia", "difference": "Butter-rich variant", "price": "₹10–40"},
        {"name": "Digestive", "brand": "McVitie's", "difference": "High-fibre option", "price": "₹40–80"},
    ],
    "chocolate": [
        {"name": "Dairy Milk", "brand": "Cadbury", "difference": "Classic milk chocolate", "price": "₹20–200"},
        {"name": "KitKat", "brand": "Nestlé", "difference": "Wafer + chocolate", "price": "₹25–150"},
        {"name": "5 Star", "brand": "Cadbury", "difference": "Caramel + nougat", "price": "₹20–100"},
    ],
    "oil": [
        {"name": "Fortune Sunflower Oil", "brand": "Adani Wilmar", "difference": "Light & healthy", "price": "₹140–170/L"},
        {"name": "Saffola Gold", "brand": "Marico", "difference": "Heart-care blend", "price": "₹160–200/L"},
        {"name": "Dhara Mustard Oil", "brand": "Mother Dairy", "difference": "Traditional flavour", "price": "₹150–180/L"},
    ],
}


def get_alternatives(product_data: dict) -> list[dict]:
    name = (product_data.get("name") or "").lower()
    category = (product_data.get("category") or "").lower()
    combined = name + " " + category

    for keyword, alts in _ALTERNATIVES_DB.items():
        if keyword in combined:
            return alts

    # Generic fallback
    cat_label = category.split(",")[0].strip().title() or "Product"
    return [
        {"name": f"Premium {cat_label}", "brand": "Leading Brand",
         "difference": "Higher quality grade", "price": "₹200–500"},
        {"name": f"Budget {cat_label}", "brand": "Value Brand",
         "difference": "Cost-effective choice", "price": "₹50–150"},
        {"name": f"Organic {cat_label}", "brand": "Organic Brand",
         "difference": "Natural / organic ingredients", "price": "₹150–350"},
    ]


# ---------------------------------------------------------------------------
# Where to buy
# ---------------------------------------------------------------------------

def get_buy_locations(product_data: dict) -> dict:
    name = (product_data.get("name") or "").lower()
    is_health = any(k in name for k in ("tablet", "capsule", "syrup", "medicine", "supplement"))

    online = [
        "Amazon India — amazon.in",
        "Flipkart — flipkart.com",
        "BigBasket — bigbasket.com",
        "Blinkit / Zepto / Swiggy Instamart (fast delivery)",
    ]
    if is_health:
        online.append("1mg / PharmEasy / Netmeds (for medicines)")

    offline = [
        "Local kirana / grocery stores",
        "D-Mart, Reliance Fresh, More Supermarket",
    ]
    if is_health:
        offline.append("Local pharmacy / chemist")
    else:
        offline.append("Big Bazaar / Spencers / departmental stores")

    return {"online": online, "offline": offline}


# ---------------------------------------------------------------------------
# Master report builder
# ---------------------------------------------------------------------------

def build_full_report(product_data: dict, reviews: list[str], amazon_data: dict | None) -> dict:
    """
    Combine all analysis functions into one report dict consumed by app.py.
    """
    sentiment = analyse_sentiment(reviews)
    pros, cons = generate_pros_cons(product_data)
    warnings = generate_health_warnings(product_data)
    rating_str = (amazon_data or {}).get("rating", "")
    score = calculate_score(product_data.get("nutrition", {}), sentiment["score"], rating_str)
    verdict = get_verdict(score)
    usage = get_usage_info(product_data)
    audience = get_target_audience(product_data)
    alternatives = get_alternatives(product_data)
    buy_locations = get_buy_locations(product_data)

    # What-is-this description: prefer scraped description, fall back to smart generic
    name = product_data.get("name") or "This product"
    brand = product_data.get("brand") or ""
    brand_str = f"by {brand} " if brand and brand.lower() not in ("unknown", "") else ""
    cat_raw = (product_data.get("category") or "consumer product").split(",")[0].strip()
    description = product_data.get("description") or (
        f"{name} {brand_str}is a popular {cat_raw} used daily across households in India. "
        f"It is widely available in supermarkets, pharmacies, and online platforms like Amazon and Flipkart."
    )

    # Why-use benefits list (5 items from pros + usage)
    why_use = pros[:3] + [
        f"Easy availability — {buy_locations['online'][0]}",
        f"Usage: {usage['frequency']}",
    ]

    return {
        # Identity
        "name": product_data.get("name", "Unknown Product"),
        "brand": product_data.get("brand", "Unknown"),
        "category": product_data.get("category", "General"),
        "quantity": product_data.get("quantity", ""),
        "image_url": product_data.get("image_url", ""),
        "price": (amazon_data or {}).get("price", "N/A"),
        "rating": rating_str,
        "amazon_url": (amazon_data or {}).get("url", ""),
        # Content
        "description": description,
        "why_use": why_use,
        "audience": audience,
        "usage": usage,
        "pros": pros,
        "cons": cons,
        "warnings": warnings,
        "ingredients": product_data.get("ingredients", ""),
        "nutrition": product_data.get("nutrition", {}),
        "nutriscore": product_data.get("nutriscore", ""),
        # Sentiment
        "sentiment": sentiment,
        "reviews_sample": reviews[:5],
        # Analysis
        "score": score,
        "verdict": verdict,
        "alternatives": alternatives,
        "buy_locations": buy_locations,
    }
