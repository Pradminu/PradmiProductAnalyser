# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Install optional barcode/OCR support (Windows needs zbar DLL separately)
pip install pyzbar pytesseract
```

## Architecture

The app is a Streamlit single-page application with a clean 4-layer pipeline:

```
Input (app.py tabs)
  → Data Fetching  (fetcher.py + scraper.py)
  → Analysis       (analyser.py)
  → Output         (app.py render_report + utils.py PDF)
```

### Layer responsibilities

**fetcher.py** — structured product data  
Hits the Open Food Facts REST API (`/api/v0/product/{barcode}.json` or `/cgi/search.pl`) and returns a normalised `product_data` dict. Also wraps `pyzbar` (barcode decode) and `pytesseract` (OCR) — both are optional; failures return `None` gracefully.

**scraper.py** — unstructured web data  
Three independent scrapers: Google search snippets (`scrape_google_description`, `get_google_reviews`), Amazon India search result (`scrape_amazon`), and a generic Open Graph / meta-tag scraper for arbitrary URLs (`scrape_url`). All use a browser-like `User-Agent` and return `None` on failure rather than raising.

**analyser.py** — rule-based engine + VADER sentiment  
`build_full_report(product_data, reviews, amazon_data)` is the single entry point that calls every sub-function and returns one flat report dict. Key sub-functions:
- `analyse_nutrition(nutrition)` — threshold rules (sodium >600 mg, sugar >20 g, calories >400, fat >20 g) → `(warnings, pros, cons)`
- `analyse_sentiment(reviews)` — VADER (falls back to keyword counting if VADER not installed)
- `calculate_score(nutrition, sentiment_score, rating_str)` — combines nutrition penalty + sentiment delta + star rating into a 0–10 float
- `get_verdict(score)` — maps score ranges to `(label, explanation, colour)` tuples

**utils.py** — output helpers  
`create_pdf_report(report)` uses `fpdf2`; returns raw `bytes` (empty bytes if fpdf2 missing).  
`format_nutrition_table(nutrition)` and `score_colour(score)` are pure display helpers.

**app.py** — Streamlit UI  
`run_analysis(product_name, url, barcode)` is the orchestration function: tries OFF → URL scrape → Amazon → Google reviews → `build_full_report`.  
`render_report(report, prefix)` renders all 13 sections; `prefix` argument lets the same function render both sides of the compare view without Streamlit widget key collisions.

### Normalised `product_data` dict shape

All fetchers/scrapers must produce (or be merged into) this shape before passing to `analyser.build_full_report`:

```python
{
  "name": str, "brand": str, "category": str,
  "ingredients": str, "image_url": str, "quantity": str,
  "labels": str, "nutriscore": str,          # "a"–"e" or ""
  "allergens": list[str],
  "nutrition": {
      "calories": float,   # kcal/100g
      "fat": float,        # g/100g
      "saturated_fat": float,
      "sugar": float,
      "sodium": float,     # mg/100g  ← OFF stores grams; fetcher.py converts
      "protein": float,
      "fiber": float,
      "carbs": float,
  },
  "source": str,           # "openfoodfacts" | "web_scrape" | "fallback"
}
```

### Data flow for each input type

| Input | Primary source | Fallback |
|---|---|---|
| Product name | OFF search by name | Google snippets stub |
| Product URL | `scrape_url` (OG tags) | — |
| Barcode image | pyzbar → OFF by barcode | — |
| Product photo | pyzbar → OFF by barcode | pytesseract OCR → name search |

Amazon data (`scrape_amazon`) and Google reviews (`get_google_reviews`) are always attempted regardless of input type and merged in `run_analysis`.
