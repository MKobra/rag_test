from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.schemas.questions import AnswerResponse, QuestionRequest
from app.services.rag_service import answer_question

router = APIRouter(prefix="/api", tags=["questions"])


@router.post("/documents/{document_id}/questions", response_model=AnswerResponse)
def ask_question(document_id: UUID, request: QuestionRequest) -> AnswerResponse:
    try:
        return answer_question(document_id, request.question)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
