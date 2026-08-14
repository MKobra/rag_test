from uuid import uuid4

from app.schemas.questions import AnswerResponse
from app.services import rag_service


def test_question_without_relevant_chunks_returns_safe_empty_answer(monkeypatch) -> None:
    document_id = uuid4()

    class EmptyStore:
        def similarity_search_with_score(self, *args, **kwargs):
            return []

    monkeypatch.setattr(rag_service, "document_exists", lambda _: True)
    monkeypatch.setattr(rag_service, "get_vector_store", lambda: EmptyStore())

    response = rag_service.answer_question(document_id, "Вопрос")

    assert response == AnswerResponse(answer="", found=False, sources=[])
