from uuid import UUID

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


class Source(BaseModel):
    chunk_id: UUID
    page: int | None = None
    quote: str


class AnswerResponse(BaseModel):
    answer: str
    found: bool
    sources: list[Source] = Field(default_factory=list)
