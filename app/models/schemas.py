from pydantic import BaseModel


class ExtractionMetadata(BaseModel):
    file_type: str
    page_count: int | None = None
    char_count: int
    extraction_method: str
    extraction_time_ms: int
    ocr_applied: bool = False
    table_count: int = 0


class ExtractionResponse(BaseModel):
    success: bool
    text: str
    metadata: ExtractionMetadata


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "santa-ai"
