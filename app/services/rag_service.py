from uuid import UUID

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.config import get_settings
from app.db import get_connection
from app.schemas.questions import AnswerResponse
from app.services.vector_store import get_vector_store


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Ты отвечаешь на вопросы только по переданному контексту.
Не используй внешние знания и не додумывай отсутствующие факты.
Если контекст не содержит ответа, верни found=false, пустой answer и пустой список sources.
Каждое утверждение в ответе должно подтверждаться одной из переданных цитат.""",
        ),
        ("human", "Контекст:\n{context}\n\nВопрос:\n{question}"),
    ]
)


def document_exists(document_id: UUID) -> bool:
    with get_connection() as connection:
        return connection.execute(
            "SELECT EXISTS (SELECT 1 FROM documents WHERE id = %s)",
            (document_id,),
        ).fetchone()[0]


def answer_question(document_id: UUID, question: str) -> AnswerResponse:
    if not document_exists(document_id):
        raise ValueError("Документ не найден")

    results = get_vector_store().similarity_search_with_score(
        question,
        k=get_settings().retrieval_k,
        filter={"document_id": str(document_id)},
    )
    relevant = [
        (document, score)
        for document, score in results
        if score <= get_settings().retrieval_distance_threshold
    ]
    if not relevant:
        return AnswerResponse(answer="", found=False, sources=[])

    context = "\n\n".join(
        f"[chunk_id={document.metadata.get('chunk_id')}; page={document.metadata.get('page')} ]\n"
        f"{document.page_content}"
        for document, _ in relevant
    )
    api_key = get_settings().groq_api_key
    if not api_key:
        raise RuntimeError("GROQ_API_KEY не настроен")

    model = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0,
    ).with_structured_output(AnswerResponse)
    response = model.invoke(PROMPT.invoke({"context": context, "question": question}))
    allowed_chunks = {document.metadata.get("chunk_id") for document, _ in relevant}
    response.sources = [
        source
        for source in response.sources
        if str(source.chunk_id) in allowed_chunks
    ]
    if not response.found or not response.sources:
        return AnswerResponse(answer="", found=False, sources=[])
    return response
