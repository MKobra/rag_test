from pydantic import BaseModel, Field, field_validator


class QuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


class Source(BaseModel):
    chunk_id: str
    page: str | int | None = None
    quote: str

    @field_validator("page", mode="before")
    @classmethod
    def _coerce_page(cls, value):
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value)
        return value


class AnswerResponse(BaseModel):
    answer: str
    found: bool | str = False
    sources: list[Source] = Field(default_factory=list)

    @field_validator("found", mode="before")
    @classmethod
    def _coerce_found(cls, value):
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "да", "yes")
        return value
