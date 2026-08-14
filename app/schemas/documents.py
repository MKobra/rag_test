from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentSummary(BaseModel):
    id: UUID
    filename: str
    topic: str
    file_type: str
    uploaded_at: datetime
    chunk_count: int


class DocumentUploadResponse(DocumentSummary):
    pass
