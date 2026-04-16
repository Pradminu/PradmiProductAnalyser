"""
scraper.py — Web scraping helpers for Amazon India, Google Search,
and generic URL product pages.  All requests use a browser-like
User-Agent to avoid trivial bot blocks.
"""

import re
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Google Search
# ---------------------------------------------------------------------------

def scrape_google_description(product_name: str) -> str:
    """Return a plain-text blurb about the product from Google search snippets."""
    try:
        query = f"{product_name} product description benefits uses"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        snippets = []
        for tag in soup.find_all(["div", "span"]):
            cls = " ".join(tag.get("class", []))
            if any(c in cls for c in ["BNeawe", "lEBKkf", "IsZvec", "VwiC3b"]):
                text = tag.get_text(separator=" ", strip=True)
                if 40 < len(text) < 400:
                    snippets.append(text)

        return " ".join(dict.fromkeys(snippets))[:800] if snippets else ""
    except Exception:
        return ""


def get_google_reviews(product_name: str) -> list[str]:
    """Scrape short review-like text snippets from a Google search."""
    try:
        query = f"{product_name} user review pros cons experience"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        reviews = []
        for tag in soup.find_all(["div", "span"]):
            text = tag.get_text(separator=" ", strip=True)
            if 30 < len(text) < 250 and any(
                w in text.lower()
                for w in ["good", "great", "bad", "recommend", "quality",
                           "love", "hate", "works", "doesn't", "excellent",
                           "poor", "average", "best", "worst", "bought"]
            ):
                reviews.append(text)

        # de-duplicate while preserving order
        seen = set()
        unique = []
        for r in reviews:
            key = r[:60]
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique[:15]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Amazon India
# ---------------------------------------------------------------------------

def scrape_amazon(product_name: str) -> dict | None:
    """
    Scrape Amazon India search results for the first matching product.
    Returns: {title, price, rating, review_count, url} or None.
    """
    try:
        search_url = (
            f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
            f"&ref=nb_sb_noss"
        )
        resp = requests.get(search_url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.find_all("div", {"data-component-type": "s-search-result"})
        for item in items[:5]:
            title_el = item.find("span", class_="a-text-normal")
            price_whole = item.find("span", class_="a-price-whole")
            price_frac = item.find("span", class_="a-price-fraction")
            rating_el = item.find("span", class_="a-icon-alt")
            review_el = item.find("span", {"aria-label": re.compile(r"\d+ ratings")})
            link_el = item.find("a", class_="a-link-normal", href=True)

            if not title_el:
                continue

            price = ""
            if price_whole:
                price = "₹" + price_whole.get_text(strip=True)
                if price_frac:
                    price += "." + price_frac.get_text(strip=True)

            return {
                "title": title_el.get_text(strip=True),
                "price": price or "N/A",
                "rating": rating_el.get_text(strip=True) if rating_el else "N/A",
                "review_count": review_el["aria-label"] if review_el else "",
                "url": "https://www.amazon.in" + link_el["href"] if link_el else "",
            }
        return None
    except Exception:
        return None


def scrape_amazon_reviews(product_url: str) -> list[str]:
    """Scrape customer review texts from an Amazon product page."""
    reviews = []
    try:
        resp = requests.get(product_url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        for span in soup.find_all("span", {"data-hook": "review-body"}):
            text = span.get_text(separator=" ", strip=True)
            if len(text) > 20:
                reviews.append(text[:300])
        return reviews[:20]
    except Exception:
        return reviews


# ---------------------------------------------------------------------------
# Generic URL scraper
# ---------------------------------------------------------------------------

def scrape_url(url: str) -> dict | None:
    """
    Generic scraper for any product URL.
    Returns a lightweight dict with name, description, price, image_url.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Title
        og_title = soup.find("meta", property="og:title")
        title = (
            og_title["content"]
            if og_title and og_title.get("content")
            else (soup.title.get_text(strip=True) if soup.title else "")
        )

        # Description
        og_desc = soup.find("meta", property="og:description")
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = (
            (og_desc["content"] if og_desc and og_desc.get("content") else "")
            or (meta_desc["content"] if meta_desc and meta_desc.get("content") else "")
        )
        if not description:
            paras = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 40]
            description = " ".join(paras[:3])[:500]

        # Price
        price = None
        for pattern in [r"₹[\d,]+\.?\d*", r"Rs\.?\s*[\d,]+", r"\$[\d,]+\.?\d*"]:
            m = re.search(pattern, resp.text)
            if m:
                price = m.group()
                break

        # Image
        og_img = soup.find("meta", property="og:image")
        image_url = og_img["content"] if og_img and og_img.get("content") else None

        return {
            "name": title[:120],
            "description": description[:600],
            "price": price,
            "image_url": image_url,
            "source": "web_scrape",
            "url": url,
        }
    except Exception:
        return None
