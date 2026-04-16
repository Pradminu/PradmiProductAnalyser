"""
app.py — Product Analyser  |  Main Streamlit application
Run:  streamlit run app.py
"""

import streamlit as st
from PIL import Image
import requests
import io

import fetcher
import scraper
import analyser
import utils

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Product Analyser",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f8f9fa; }

    /* Section cards */
    .report-card {
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }

    /* Score badge */
    .score-badge {
        display: inline-block;
        font-size: 2.4rem;
        font-weight: 800;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        line-height: 80px;
        text-align: center;
        color: white;
    }

    /* Pros / Cons list items */
    .pro-item  { color: #198754; font-weight: 500; }
    .con-item  { color: #dc3545; font-weight: 500; }
    .warn-item { color: #fd7e14; font-weight: 500; }

    /* Verdict box */
    .verdict-green  { background:#d1e7dd; border-left:5px solid #198754; padding:12px; border-radius:8px; }
    .verdict-blue   { background:#cfe2ff; border-left:5px solid #0d6efd; padding:12px; border-radius:8px; }
    .verdict-orange { background:#fff3cd; border-left:5px solid #fd7e14; padding:12px; border-radius:8px; }
    .verdict-red    { background:#f8d7da; border-left:5px solid #dc3545; padding:12px; border-radius:8px; }

    /* Input tab styling */
    .stTabs [data-baseweb="tab"] { font-size: 0.95rem; font-weight: 600; }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "report" not in st.session_state:
    st.session_state.report = None
if "compare_report" not in st.session_state:
    st.session_state.compare_report = None


# ---------------------------------------------------------------------------
# Helper — fetch + analyse pipeline
# ---------------------------------------------------------------------------

def run_analysis(product_name: str = "", url: str = "", barcode: str = "") -> dict | None:
    """
    Orchestrate data fetching → scraping → analysis and return a full report dict.
    """
    product_data = None

    # 1. Open Food Facts
    with st.spinner("Searching product database…"):
        if barcode:
            product_data = fetcher.fetch_by_barcode(barcode)
        if not product_data and product_name:
            product_data = fetcher.fetch_by_name(product_name)

    # 2. URL scrape (merges into product_data)
    if url:
        with st.spinner("Scraping product page…"):
            scraped = scraper.scrape_url(url)
            if scraped:
                if product_data:
                    # Merge: prefer OFF data but fill gaps from scrape
                    product_data.setdefault("price", scraped.get("price"))
                    if not product_data.get("image_url"):
                        product_data["image_url"] = scraped.get("image_url")
                    if not product_data.get("description"):
                        product_data["description"] = scraped.get("description")
                else:
                    product_data = {
                        "name": scraped.get("name") or product_name or "Unknown Product",
                        "brand": "Unknown",
                        "category": "General",
                        "ingredients": "",
                        "image_url": scraped.get("image_url", ""),
                        "quantity": "",
                        "labels": "",
                        "nutriscore": "",
                        "allergens": [],
                        "nutrition": {},
                        "description": scraped.get("description", ""),
                        "price": scraped.get("price", ""),
                        "source": "web_scrape",
                    }

    # 3. Fallback: minimal stub so we can still render something
    if not product_data:
        if not product_name:
            return None
        product_data = {
            "name": product_name,
            "brand": "Unknown",
            "category": "General",
            "ingredients": "",
            "image_url": "",
            "quantity": "",
            "labels": "",
            "nutriscore": "",
            "allergens": [],
            "nutrition": {},
            "source": "fallback",
        }

    # 4. Amazon price + rating
    with st.spinner("Checking Amazon India for price & rating…"):
        search_name = product_data.get("name") or product_name
        amazon_data = scraper.scrape_amazon(search_name)

    # 5. Reviews (Google snippets)
    with st.spinner("Gathering review data…"):
        reviews = scraper.get_google_reviews(product_data.get("name") or product_name)

    # 6. Build full report
    with st.spinner("Analysing product…"):
        report = analyser.build_full_report(product_data, reviews, amazon_data)

    return report


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def render_score_meter(score: float):
    colour = utils.score_colour(score)
    pct = int(score / 10 * 100)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:20px;margin-bottom:8px;">
        <div class="score-badge" style="background:{colour};">{score}</div>
        <div style="flex:1;">
            <div style="font-size:0.85rem;color:#6c757d;margin-bottom:4px;">Overall Score</div>
            <div style="background:#e9ecef;border-radius:10px;height:16px;">
                <div style="background:{colour};width:{pct}%;height:16px;
                            border-radius:10px;transition:width 0.5s;"></div>
            </div>
            <div style="font-size:0.8rem;color:{colour};margin-top:3px;font-weight:600;">
                {score} / 10
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def render_sentiment_bar(sentiment: dict):
    pos = sentiment.get("positive", 0)
    neg = sentiment.get("negative", 0)
    neu = sentiment.get("neutral", 0)
    st.markdown(f"""
    <div style="margin:8px 0;">
        <div style="display:flex;height:20px;border-radius:10px;overflow:hidden;">
            <div style="background:#198754;width:{pos}%;"></div>
            <div style="background:#6c757d;width:{neu}%;"></div>
            <div style="background:#dc3545;width:{neg}%;"></div>
        </div>
        <div style="display:flex;gap:16px;font-size:0.82rem;margin-top:4px;">
            <span style="color:#198754;">✅ Positive {pos}%</span>
            <span style="color:#6c757d;">➖ Neutral {neu}%</span>
            <span style="color:#dc3545;">❌ Negative {neg}%</span>
        </div>
    </div>""", unsafe_allow_html=True)


def render_report(report: dict, prefix: str = ""):
    """Render a full product report. prefix differentiates compare columns."""

    # ------------------------------------------------------------------ #
    # Top section: image + identity + score
    # ------------------------------------------------------------------ #
    col_img, col_info = st.columns([1, 3])

    with col_img:
        img_url = report.get("image_url")
        if img_url:
            try:
                resp = requests.get(img_url, timeout=8)
                img = Image.open(io.BytesIO(resp.content))
                st.image(img, use_container_width=True)
            except Exception:
                st.image("https://via.placeholder.com/200x200?text=No+Image",
                         use_container_width=True)
        else:
            st.markdown("📦", unsafe_allow_html=False)

    with col_info:
        st.markdown(f"### {report.get('name', 'Unknown Product')}")
        meta_cols = st.columns(3)
        meta_cols[0].metric("Brand", report.get("brand", "N/A"))
        meta_cols[1].metric("Price", report.get("price", "N/A"))
        meta_cols[2].metric("Rating", report.get("rating", "N/A"))
        st.caption(f"Category: {(report.get('category') or '')[:80]}")
        if report.get("quantity"):
            st.caption(f"Pack size: {report['quantity']}")
        render_score_meter(report.get("score", 5.0))

    st.divider()

    # ------------------------------------------------------------------ #
    # 1. What is this product?
    # ------------------------------------------------------------------ #
    with st.expander("📌 WHAT IS THIS PRODUCT?", expanded=True):
        st.write(report.get("description", "Description not available."))

    # ------------------------------------------------------------------ #
    # 2. Why should you use it?
    # ------------------------------------------------------------------ #
    with st.expander("✅ WHY SHOULD YOU USE IT?", expanded=True):
        for item in report.get("why_use", []):
            st.markdown(f'<div class="pro-item">✔ {item}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # 3. Who is it best for?
    # ------------------------------------------------------------------ #
    with st.expander("🎯 WHO IS IT BEST FOR?"):
        for person in report.get("audience", []):
            st.markdown(f"👤 {person}")

    # ------------------------------------------------------------------ #
    # 4. How to use it
    # ------------------------------------------------------------------ #
    with st.expander("📖 HOW TO USE IT"):
        usage = report.get("usage", {})
        if usage.get("instructions"):
            st.markdown("**Instructions:**")
            for step in usage["instructions"]:
                st.markdown(f"• {step}")
        cols = st.columns(3)
        cols[0].info(f"**Frequency**\n\n{usage.get('frequency', 'N/A')}")
        cols[1].info(f"**Best Time**\n\n{usage.get('best_time', 'N/A')}")
        cols[2].info(f"**Storage**\n\n{usage.get('storage', 'N/A')}")

    # ------------------------------------------------------------------ #
    # 5 & 6. Pros & Cons (side by side)
    # ------------------------------------------------------------------ #
    with st.expander("⭐ PROS & CONS", expanded=True):
        p_col, c_col = st.columns(2)
        with p_col:
            st.markdown("**✅ Pros**")
            for pro in report.get("pros", []):
                st.markdown(f'<div class="pro-item">+ {pro}</div>', unsafe_allow_html=True)
        with c_col:
            st.markdown("**❌ Cons**")
            for con in report.get("cons", []):
                st.markdown(f'<div class="con-item">– {con}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # 7. Health warnings
    # ------------------------------------------------------------------ #
    with st.expander("🚫 HEALTH WARNINGS & RISKS"):
        for w in report.get("warnings", []):
            st.markdown(f'<div class="warn-item">⚠️ {w}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # 8. Ingredients + Nutrition
    # ------------------------------------------------------------------ #
    with st.expander("🧪 KEY INGREDIENTS / NUTRITION"):
        ingredients = report.get("ingredients", "")
        if ingredients:
            st.markdown("**Ingredients:**")
            st.write(ingredients[:500] + ("…" if len(ingredients) > 500 else ""))
            st.divider()

        nutrition = report.get("nutrition", {})
        nut_table = utils.format_nutrition_table(nutrition)
        if nut_table:
            st.markdown("**Nutrition Facts (per 100 g / 100 ml):**")
            nut_cols = st.columns(4)
            for i, (label, value) in enumerate(nut_table.items()):
                nut_cols[i % 4].metric(label, value)

        nutriscore = report.get("nutriscore", "")
        if nutriscore:
            colours = {"a": "🟢", "b": "🟡", "c": "🟠", "d": "🔴", "e": "🔴"}
            emoji = colours.get(nutriscore.lower(), "⚪")
            st.markdown(f"**Nutri-Score:** {emoji} Grade **{nutriscore.upper()}**")

    # ------------------------------------------------------------------ #
    # 9. Review Sentiment
    # ------------------------------------------------------------------ #
    with st.expander("🌍 REVIEW SENTIMENT SUMMARY"):
        sentiment = report.get("sentiment", {})
        st.markdown(f"**Overall Sentiment: {sentiment.get('overall', 'N/A')}**")
        render_sentiment_bar(sentiment)

        reviews = report.get("reviews_sample", [])
        if reviews:
            st.markdown("**Sample reviews:**")
            for r in reviews[:3]:
                st.markdown(f"> {r[:200]}")

    # ------------------------------------------------------------------ #
    # 10. Alternatives
    # ------------------------------------------------------------------ #
    with st.expander("🔄 ALTERNATIVES / COMPETITORS"):
        import pandas as pd
        alts = report.get("alternatives", [])
        if alts:
            df = pd.DataFrame(alts).rename(columns={
                "name": "Product", "brand": "Brand",
                "difference": "Key Difference", "price": "Est. Price"
            })
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------ #
    # 11. Verdict
    # ------------------------------------------------------------------ #
    verdict = report.get("verdict", ("N/A", "No verdict available.", "gray"))
    colour_map = {
        "green": "verdict-green",
        "blue": "verdict-blue",
        "orange": "verdict-orange",
        "red": "verdict-red",
    }
    css_class = colour_map.get(verdict[2], "verdict-orange")
    st.markdown(f"""
    <div class="{css_class}">
        <div style="font-size:1.2rem;font-weight:700;margin-bottom:6px;">{verdict[0]}</div>
        <div>{verdict[1]}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # 12. Where to buy
    # ------------------------------------------------------------------ #
    with st.expander("🛒 WHERE TO BUY"):
        buy = report.get("buy_locations", {})
        bc1, bc2 = st.columns(2)
        with bc1:
            st.markdown("**🌐 Online**")
            for loc in buy.get("online", []):
                st.markdown(f"• {loc}")
        with bc2:
            st.markdown("**🏪 Offline**")
            for loc in buy.get("offline", []):
                st.markdown(f"• {loc}")

    # ------------------------------------------------------------------ #
    # PDF Download
    # ------------------------------------------------------------------ #
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = utils.create_pdf_report(report)
    if pdf_bytes:
        safe_name = (report.get("name") or "product").replace(" ", "_")[:30]
        st.download_button(
            label="📥 Download Full Report as PDF",
            data=pdf_bytes,
            file_name=f"{safe_name}_analysis.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.info("Install `fpdf2` to enable PDF download (`pip install fpdf2`).")


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------

def main():
    # Header
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px;">
        <h1 style="font-size:2.4rem;font-weight:800;color:#212529;">🔍 Product Analyser</h1>
        <p style="color:#6c757d;font-size:1.05rem;">
            Analyse any product — food, beauty, health, electronics & more.<br>
            Enter a name, URL, scan a barcode, or upload a photo.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ------------------------------------------------------------------ #
    # Input section
    # ------------------------------------------------------------------ #
    st.markdown("### 🛒 How would you like to search?")
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔤 Product Name", "🔗 Product URL", "📷 Barcode Image", "🖼️ Product Photo"
    ])

    product_name = url = barcode = ""

    # Tab 1 — Name
    with tab1:
        st.markdown("Type the product name (e.g. *Maggi Noodles*, *Dove Soap*, *Himalaya Face Wash*)")
        product_name_input = st.text_input(
            "Product Name", placeholder="e.g. Maggi 2-Minute Noodles",
            key="name_input", label_visibility="collapsed"
        )
        if st.button("🔍 Analyse Product", key="btn_name", use_container_width=True, type="primary"):
            if product_name_input.strip():
                product_name = product_name_input.strip()
                with st.spinner("Fetching and analysing…"):
                    st.session_state.report = run_analysis(product_name=product_name)
            else:
                st.warning("Please enter a product name.")

    # Tab 2 — URL
    with tab2:
        st.markdown("Paste any product URL from Amazon, Flipkart, brand website, etc.")
        url_input = st.text_input(
            "Product URL", placeholder="https://www.amazon.in/dp/...",
            key="url_input", label_visibility="collapsed"
        )
        if st.button("🔍 Analyse URL", key="btn_url", use_container_width=True, type="primary"):
            if url_input.strip():
                url = url_input.strip()
                with st.spinner("Fetching and analysing…"):
                    st.session_state.report = run_analysis(url=url)
            else:
                st.warning("Please enter a URL.")

    # Tab 3 — Barcode
    with tab3:
        st.markdown("Upload an image of the product barcode (EAN / UPC).")
        barcode_file = st.file_uploader(
            "Upload barcode image", type=["jpg", "jpeg", "png", "webp"],
            key="barcode_upload", label_visibility="collapsed"
        )
        if barcode_file:
            bc_img = Image.open(barcode_file)
            st.image(bc_img, width=300, caption="Uploaded barcode image")
            if st.button("🔍 Scan & Analyse", key="btn_barcode", use_container_width=True, type="primary"):
                with st.spinner("Reading barcode…"):
                    barcode = fetcher.read_barcode_from_image(bc_img)
                if barcode:
                    st.success(f"Barcode detected: **{barcode}**")
                    with st.spinner("Fetching and analysing…"):
                        st.session_state.report = run_analysis(barcode=barcode)
                else:
                    st.error(
                        "Could not read barcode. "
                        "Make sure `pyzbar` and the zbar DLL are installed, "
                        "or try a clearer image."
                    )

    # Tab 4 — Photo
    with tab4:
        st.markdown("Upload a photo of the product label or packaging.")
        photo_file = st.file_uploader(
            "Upload product photo", type=["jpg", "jpeg", "png", "webp"],
            key="photo_upload", label_visibility="collapsed"
        )
        if photo_file:
            ph_img = Image.open(photo_file)
            st.image(ph_img, width=300, caption="Uploaded product photo")
            if st.button("🔍 Read & Analyse", key="btn_photo", use_container_width=True, type="primary"):
                # Try barcode first
                with st.spinner("Checking for barcode…"):
                    detected_bc = fetcher.read_barcode_from_image(ph_img)
                if detected_bc:
                    st.success(f"Barcode found: **{detected_bc}**")
                    barcode = detected_bc
                else:
                    # Fall back to OCR
                    with st.spinner("Reading product label text (OCR)…"):
                        ocr_text = fetcher.read_text_from_image(ph_img)
                    if ocr_text:
                        product_name = fetcher.guess_product_name_from_ocr(ocr_text)
                        st.info(f"Product name detected: **{product_name}**")
                    else:
                        st.warning(
                            "Could not read text. "
                            "Make sure `pytesseract` and Tesseract binary are installed."
                        )

                if barcode or product_name:
                    with st.spinner("Fetching and analysing…"):
                        st.session_state.report = run_analysis(
                            product_name=product_name, barcode=barcode
                        )

    # ------------------------------------------------------------------ #
    # Report output
    # ------------------------------------------------------------------ #
    if st.session_state.report:
        st.divider()
        st.markdown("## 📊 Analysis Report")
        render_report(st.session_state.report)

        # ---------------------------------------------------------------- #
        # Compare feature
        # ---------------------------------------------------------------- #
        st.divider()
        st.markdown("## 🔄 Compare with Another Product")
        compare_name = st.text_input(
            "Enter a second product to compare",
            placeholder="e.g. Top Ramen Noodles",
            key="compare_input"
        )
        if st.button("⚖️ Compare", key="btn_compare", use_container_width=True):
            if compare_name.strip():
                with st.spinner("Analysing comparison product…"):
                    st.session_state.compare_report = run_analysis(product_name=compare_name.strip())
            else:
                st.warning("Enter a product name to compare.")

        if st.session_state.compare_report:
            st.markdown("### Side-by-side Comparison")
            left_col, right_col = st.columns(2)

            report1 = st.session_state.report
            report2 = st.session_state.compare_report

            with left_col:
                st.markdown(f"#### {report1.get('name', 'Product 1')}")
                render_report(report1, prefix="left_")

            with right_col:
                st.markdown(f"#### {report2.get('name', 'Product 2')}")
                render_report(report2, prefix="right_")

    # Footer
    st.markdown("""
    <div style="text-align:center;color:#adb5bd;font-size:0.8rem;margin-top:40px;">
        Product Analyser — Data from Open Food Facts, Amazon India & Google.<br>
        For informational purposes only. Always verify with official product information.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
