from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.schemas.questions import AnswerResponse, QuestionRequest
from app.services.rag_service import answer_question
from app.auth import get_current_user_id
from app.config import get_settings
from app.limits import enforce_limit
from app.services.chat_service import conversation_document

router = APIRouter(prefix="/api", tags=["questions"])


@router.post("/conversations/{conversation_id}/questions", response_model=AnswerResponse)
def ask_question(
    conversation_id: UUID,
    request: QuestionRequest,
    user_id=Depends(get_current_user_id),
) -> AnswerResponse:
    try:
        enforce_limit(f"questions:{user_id}", get_settings().max_questions_per_minute, 60)
        document_id = conversation_document(conversation_id, user_id)
        return answer_question(document_id, conversation_id, user_id, request.question)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
