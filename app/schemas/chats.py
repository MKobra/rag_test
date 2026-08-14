from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    id: UUID
    title: str
    created_at: datetime


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    sources: list[dict] = Field(default_factory=list)
    created_at: datetime


class ConversationResponse(ConversationSummary):
    messages: list[MessageResponse]
