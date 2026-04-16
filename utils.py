"""
utils.py — PDF report generation and miscellaneous helpers.
"""

import io
from datetime import datetime


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def create_pdf_report(report: dict) -> bytes:
    """
    Generate a PDF Product Analysis Report using fpdf2.
    Returns raw bytes suitable for st.download_button.
    """
    try:
        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 14)
                self.set_text_color(33, 37, 41)
                self.cell(0, 10, "Product Analysis Report", align="C", new_x="LMARGIN", new_y="NEXT")
                self.set_font("Helvetica", size=9)
                self.set_text_color(108, 117, 125)
                self.cell(0, 6, f"Generated on {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
                          align="C", new_x="LMARGIN", new_y="NEXT")
                self.ln(3)
                self.set_draw_color(220, 220, 220)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(4)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 10, f"Page {self.page_no()}", align="C")

        pdf = PDF()
        pdf.set_margins(15, 20, 15)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        def section_title(text: str):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(13, 110, 253)
            pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(13, 110, 253)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
            pdf.ln(2)
            pdf.set_text_color(33, 37, 41)

        def body_text(text: str):
            pdf.set_font("Helvetica", size=10)
            pdf.set_text_color(33, 37, 41)
            safe = text.encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(0, 6, safe)
            pdf.ln(1)

        def bullet_list(items: list, colour=(33, 37, 41)):
            pdf.set_font("Helvetica", size=10)
            pdf.set_text_color(*colour)
            for item in items:
                safe = f"  • {item}".encode("latin-1", errors="replace").decode("latin-1")
                pdf.multi_cell(0, 6, safe)
            pdf.set_text_color(33, 37, 41)
            pdf.ln(2)

        # ---- Product Identity ----
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(33, 37, 41)
        name_safe = (report.get("name") or "Unknown").encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 9, name_safe)
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(108, 117, 125)
        pdf.cell(0, 6,
                 f"Brand: {report.get('brand', 'N/A')}   |   "
                 f"Category: {(report.get('category') or '')[:50]}   |   "
                 f"Price: {report.get('price', 'N/A')}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(40, 167, 69)
        pdf.cell(0, 8, f"Overall Score: {report.get('score', 'N/A')} / 10",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # ---- Description ----
        section_title("WHAT IS THIS PRODUCT?")
        body_text(report.get("description") or "")

        # ---- Why Use ----
        section_title("WHY SHOULD YOU USE IT?")
        bullet_list(report.get("why_use") or [])

        # ---- Who is it for ----
        section_title("WHO IS IT BEST FOR?")
        bullet_list(report.get("audience") or [])

        # ---- How to Use ----
        usage = report.get("usage") or {}
        section_title("HOW TO USE IT")
        bullet_list(usage.get("instructions") or [])
        body_text(f"Frequency: {usage.get('frequency', '')}")
        body_text(f"Best time: {usage.get('best_time', '')}")
        body_text(f"Storage: {usage.get('storage', '')}")

        # ---- Pros ----
        section_title("PROS")
        bullet_list(report.get("pros") or [], colour=(40, 167, 69))

        # ---- Cons ----
        section_title("CONS")
        bullet_list(report.get("cons") or [], colour=(220, 53, 69))

        # ---- Warnings ----
        section_title("HEALTH WARNINGS & RISKS")
        bullet_list(report.get("warnings") or [], colour=(255, 153, 0))

        # ---- Ingredients ----
        ingredients = (report.get("ingredients") or "").strip()
        if ingredients:
            section_title("KEY INGREDIENTS / COMPONENTS")
            body_text(ingredients[:400])

        # ---- Sentiment ----
        sentiment = report.get("sentiment") or {}
        section_title("REVIEW SENTIMENT SUMMARY")
        body_text(
            f"Overall Sentiment: {sentiment.get('overall', 'N/A')}   |   "
            f"Positive: {sentiment.get('positive', 0)}%   "
            f"Negative: {sentiment.get('negative', 0)}%   "
            f"Neutral: {sentiment.get('neutral', 0)}%"
        )

        # ---- Verdict ----
        verdict = report.get("verdict") or ("N/A", "No verdict available.", "gray")
        section_title("VERDICT")
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(33, 37, 41)
        label_safe = verdict[0].encode("latin-1", errors="replace").decode("latin-1")
        pdf.cell(0, 7, label_safe, new_x="LMARGIN", new_y="NEXT")
        body_text(verdict[1])

        # ---- Where to Buy ----
        section_title("WHERE TO BUY")
        buy = report.get("buy_locations") or {}
        if buy.get("online"):
            body_text("Online:")
            bullet_list(buy["online"])
        if buy.get("offline"):
            body_text("Offline:")
            bullet_list(buy["offline"])

        return bytes(pdf.output())

    except ImportError:
        return b""
    except Exception:
        return b""


# ---------------------------------------------------------------------------
# Nutrition formatting helper
# ---------------------------------------------------------------------------

def format_nutrition_table(nutrition: dict) -> dict:
    """Return a display-ready {label: value_with_unit} dict."""
    mapping = [
        ("calories",     "Calories",         "kcal"),
        ("carbs",        "Carbohydrates",     "g"),
        ("sugar",        "of which Sugars",   "g"),
        ("fat",          "Total Fat",         "g"),
        ("saturated_fat","Saturated Fat",     "g"),
        ("protein",      "Protein",           "g"),
        ("fiber",        "Dietary Fiber",     "g"),
        ("sodium",       "Sodium",            "mg"),
    ]
    result = {}
    for key, label, unit in mapping:
        val = nutrition.get(key)
        if val is not None and val != 0:
            result[label] = f"{float(val):.1f} {unit}"
    return result


# ---------------------------------------------------------------------------
# Score colour helper
# ---------------------------------------------------------------------------

def score_colour(score: float) -> str:
    """Return a hex colour string based on the score."""
    if score >= 7.5:
        return "#28a745"   # green
    elif score >= 6.0:
        return "#0d6efd"   # blue
    elif score >= 4.5:
        return "#fd7e14"   # orange
    else:
        return "#dc3545"   # red
