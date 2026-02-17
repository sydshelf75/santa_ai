import logging

import pymupdf

logger = logging.getLogger("santa-ai")

# If a page yields fewer chars than this, it's likely scanned/image-based
SPARSE_TEXT_THRESHOLD = 50

# Try importing OCR dependencies — graceful if Tesseract isn't installed
try:
    import pytesseract
    from PIL import Image
    import shutil

    # Auto-detect Tesseract path on Windows if not on PATH
    if shutil.which("tesseract") is None:
        import platform
        if platform.system() == "Windows":
            _win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            import os
            if os.path.isfile(_win_path):
                pytesseract.pytesseract.tesseract_cmd = _win_path

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("pytesseract or Pillow not installed — OCR disabled")


def extract_pdf(data: bytes) -> tuple[str, int, str, bool, int]:
    """Extract text from PDF bytes using PyMuPDF + OCR fallback.

    Returns (text, page_count, method, ocr_applied, table_count).
    """
    doc = pymupdf.open(stream=data, filetype="pdf")
    page_texts: list[str] = []
    ocr_pages = 0
    total_tables = 0

    for page in doc:
        # --- text-layer extraction ---
        text = page.get_text().strip()

        # --- OCR fallback for sparse / scanned pages ---
        if len(text) < SPARSE_TEXT_THRESHOLD and OCR_AVAILABLE:
            ocr_text = _ocr_page(page)
            if ocr_text and len(ocr_text) > len(text):
                text = ocr_text
                ocr_pages += 1

        # --- structured table extraction ---
        try:
            found = page.find_tables()
            for table in found.tables:
                md = _table_to_markdown(table.extract())
                if md:
                    text += "\n\n" + md
                    total_tables += 1
        except Exception:
            pass  # table detection can fail on some pages

        page_texts.append(text)

    page_count = len(doc)
    doc.close()

    combined = "\n\n".join(t for t in page_texts if t)

    if ocr_pages > 0:
        method = f"pymupdf+ocr({ocr_pages}/{page_count})"
    else:
        method = "pymupdf"

    return combined, page_count, method, ocr_pages > 0, total_tables


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ocr_page(page, dpi: int = 300) -> str:
    """Render a page to an image and run Tesseract OCR."""
    try:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text: str = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as exc:
        logger.debug("OCR failed for page: %s", exc)
        return ""


def _table_to_markdown(rows: list[list[str | None]]) -> str:
    """Convert a table (list of rows) to a markdown table string."""
    if not rows:
        return ""

    # Clean cells
    clean: list[list[str]] = []
    for row in rows:
        clean.append([(cell or "").strip().replace("\n", " ") for cell in row])

    if not clean:
        return ""

    col_count = max(len(r) for r in clean)

    # Pad rows to same length
    for row in clean:
        while len(row) < col_count:
            row.append("")

    lines: list[str] = []
    # Header
    lines.append("| " + " | ".join(clean[0]) + " |")
    lines.append("| " + " | ".join("---" for _ in range(col_count)) + " |")
    # Body
    for row in clean[1:]:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)
