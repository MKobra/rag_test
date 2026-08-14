from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user_id
from app.schemas.chats import ConversationResponse, ConversationSummary
from app.services.chat_service import create_conversation, get_conversation, list_conversations

router = APIRouter(prefix="/api", tags=["chats"])


@router.get("/documents/{document_id}/conversations", response_model=list[ConversationSummary])
def get_chats(document_id: UUID, user_id=Depends(get_current_user_id)) -> list[dict]:
    try:
        return list_conversations(document_id, user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/documents/{document_id}/conversations", response_model=ConversationSummary, status_code=201)
def new_chat(document_id: UUID, user_id=Depends(get_current_user_id)) -> dict:
    try:
        return create_conversation(document_id, user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def conversation(conversation_id: UUID, user_id=Depends(get_current_user_id)) -> dict:
    try:
        return get_conversation(conversation_id, user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
