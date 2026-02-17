import time

from app.models.schemas import ExtractionResponse, ExtractionMetadata
from app.services.pdf_extractor import extract_pdf
from app.services.docx_extractor import extract_docx
from app.services.text_extractor import extract_text

SUPPORTED_TYPES = {"pdf", "docx", "doc", "txt", "text", "md", "markdown"}


def extract(data: bytes, file_type: str) -> ExtractionResponse:
    """Route extraction to the correct parser based on file type."""
    ft = file_type.lower().lstrip(".")
    if ft not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {file_type}")

    start = time.perf_counter()
    page_count: int | None = None
    ocr_applied = False
    table_count = 0

    if ft == "pdf":
        text, page_count, method, ocr_applied, table_count = extract_pdf(data)
    elif ft in ("docx", "doc"):
        text = extract_docx(data)
        method = "python-docx"
    else:
        text = extract_text(data)
        method = "chardet"

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return ExtractionResponse(
        success=True,
        text=text,
        metadata=ExtractionMetadata(
            file_type=ft,
            page_count=page_count,
            char_count=len(text),
            extraction_method=method,
            extraction_time_ms=elapsed_ms,
            ocr_applied=ocr_applied,
            table_count=table_count,
        ),
    )
