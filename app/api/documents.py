from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.document_service import index_file, list_documents
from app.schemas.documents import DocumentSummary, DocumentUploadResponse

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/documents", response_model=list[DocumentSummary])
def get_documents() -> list[dict]:
    return list_documents()


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename or Path(file.filename).suffix.lower() not in {".txt", ".docx", ".pdf"}:
        raise HTTPException(status_code=400, detail="Поддерживаются только TXT, DOCX и PDF")
    try:
        content = await file.read()
        return index_file(file.filename, content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
