import chardet


def extract_text(data: bytes) -> str:
    """Extract text from plain text / markdown bytes with encoding detection."""
    detection = chardet.detect(data)
    encoding = detection.get("encoding") or "utf-8"
    return data.decode(encoding, errors="replace")
