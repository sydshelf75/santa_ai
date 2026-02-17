from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.config import settings
from app.models.schemas import ExtractionResponse, ErrorResponse
from app.services.extractor import extract

router = APIRouter()


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
)
async def extract_document(
    file: UploadFile = File(...),
    file_type: str = Form(default=""),
):
    # Determine file type from form field or filename extension
    ft = file_type.strip()
    if not ft and file.filename:
        ft = file.filename.rsplit(".", 1)[-1] if "." in file.filename else ""
    if not ft:
        raise HTTPException(status_code=400, detail="Cannot determine file type. Provide file_type or a filename with an extension.")

    data = await file.read()

    if len(data) > settings.max_file_size_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit.")

    try:
        result = extract(data, ft)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result
