"""
fetcher.py — Product data fetching from Open Food Facts API,
barcode image reading, and OCR text extraction from product photos.
"""

import requests
from PIL import Image


OPENFOODFACTS_API = "https://world.openfoodfacts.org/api/v0/product/{}.json"
OPENFOODFACTS_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"


def fetch_by_barcode(barcode: str) -> dict | None:
    """Fetch product data from Open Food Facts using barcode number."""
    try:
        url = OPENFOODFACTS_API.format(barcode.strip())
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == 1 and data.get("product"):
            return parse_off_product(data["product"])
        return None
    except Exception:
        return None


def fetch_by_name(name: str) -> dict | None:
    """Search Open Food Facts by product name — returns best match."""
    try:
        params = {
            "search_terms": name,
            "json": 1,
            "page_size": 5,
            "sort_by": "unique_scans_n",
        }
        response = requests.get(OPENFOODFACTS_SEARCH, params=params, timeout=10)
        data = response.json()
        products = data.get("products", [])
        # Pick the product with the most complete data
        for product in products:
            if product.get("product_name") and product.get("ingredients_text"):
                return parse_off_product(product)
        if products:
            return parse_off_product(products[0])
        return None
    except Exception:
        return None


def parse_off_product(product: dict) -> dict:
    """Normalise an Open Food Facts product dict into the app's standard format."""
    nutriments = product.get("nutriments", {})

    # Sodium in OFF is stored in grams; convert to mg for rules engine
    sodium_g = nutriments.get("sodium_100g", 0) or 0
    sodium_mg = sodium_g * 1000

    return {
        "name": product.get("product_name") or product.get("product_name_en") or "Unknown Product",
        "brand": product.get("brands", "Unknown"),
        "category": product.get("categories", "General"),
        "ingredients": product.get("ingredients_text", ""),
        "image_url": product.get("image_front_url") or product.get("image_url", ""),
        "quantity": product.get("quantity", ""),
        "labels": product.get("labels", ""),
        "nutriscore": product.get("nutriscore_grade", ""),
        "allergens": product.get("allergens_tags", []),
        "nutrition": {
            "calories": nutriments.get("energy-kcal_100g") or nutriments.get("energy_100g", 0) or 0,
            "fat": nutriments.get("fat_100g", 0) or 0,
            "saturated_fat": nutriments.get("saturated-fat_100g", 0) or 0,
            "sugar": nutriments.get("sugars_100g", 0) or 0,
            "sodium": sodium_mg,
            "protein": nutriments.get("proteins_100g", 0) or 0,
            "fiber": nutriments.get("fiber_100g", 0) or 0,
            "carbs": nutriments.get("carbohydrates_100g", 0) or 0,
        },
        "source": "openfoodfacts",
    }


def read_barcode_from_image(image: Image.Image) -> str | None:
    """
    Decode the first barcode found in a PIL Image.
    Requires: pyzbar (pip install pyzbar) and zbar DLL on Windows.
    """
    try:
        from pyzbar.pyzbar import decode
        barcodes = decode(image)
        if barcodes:
            return barcodes[0].data.decode("utf-8")
        return None
    except ImportError:
        return None
    except Exception:
        return None


def read_text_from_image(image: Image.Image) -> str | None:
    """
    Extract text from a product label photo using Tesseract OCR.
    Requires: pytesseract + Tesseract binary installed on the system.
    """
    try:
        import pytesseract
        text = pytesseract.image_to_string(image)
        return text.strip() if text.strip() else None
    except ImportError:
        return None
    except Exception:
        return None


def guess_product_name_from_ocr(ocr_text: str) -> str:
    """Extract a likely product name from raw OCR text (first non-empty line)."""
    if not ocr_text:
        return ""
    lines = [l.strip() for l in ocr_text.splitlines() if len(l.strip()) > 3]
    return lines[0] if lines else ""
