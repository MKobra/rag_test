from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth import get_current_user_id
from app.config import get_settings
from app.limits import enforce_limit
from app.services.document_service import index_file, list_documents
from app.schemas.documents import DocumentSummary, DocumentUploadResponse

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/documents", response_model=list[DocumentSummary])
def get_documents(user_id=Depends(get_current_user_id)) -> list[dict]:
    return list_documents(user_id)


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...), user_id=Depends(get_current_user_id)
) -> dict:
    if not file.filename or Path(file.filename).suffix.lower() not in {".txt", ".docx", ".pdf"}:
        raise HTTPException(status_code=400, detail="Поддерживаются только TXT, DOCX и PDF")
    try:
        enforce_limit(f"uploads:{user_id}", get_settings().max_uploads_per_hour, 3600)
        content = await file.read(get_settings().max_upload_size_bytes + 1)
        if len(content) > get_settings().max_upload_size_bytes:
            raise HTTPException(status_code=413, detail="Файл превышает лимит 10 МБ")
        return index_file(file.filename, content, user_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
