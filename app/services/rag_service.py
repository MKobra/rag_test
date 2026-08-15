from uuid import UUID

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.config import get_settings
from app.db import get_connection
from app.schemas.questions import AnswerResponse
from app.services.vector_store import get_vector_store
from app.services.chat_service import recent_messages, save_message


NO_ANSWER = "В документе не найдено информации по этому вопросу."


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Ты отвечаешь на вопросы только по переданному контексту.
Не используй внешние знания и не додумывай отсутствующие факты.
Если контекст не содержит ответа, верни found=false, пустой answer и пустой список sources.
Каждое утверждение в ответе должно подтверждаться одной из переданных цитат.""",
        ),
        ("human", "История диалога:\n{history}\n\nКонтекст документа:\n{context}\n\nНовый вопрос:\n{question}"),
    ]
)


def document_exists(document_id: UUID) -> bool:
    with get_connection() as connection:
        return connection.execute(
            "SELECT EXISTS (SELECT 1 FROM documents WHERE id = %s)",
            (document_id,),
        ).fetchone()[0]


def answer_question(document_id: UUID, conversation_id: UUID, owner_id: UUID, question: str) -> AnswerResponse:
    if not document_exists(document_id):
        raise ValueError("Документ не найден")
    history = recent_messages(conversation_id, owner_id)
    save_message(conversation_id, "user", question, [])

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
        response = AnswerResponse(answer=NO_ANSWER, found=False, sources=[])
        save_message(conversation_id, "assistant", response.answer, [])
        return response

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
        model="openai/gpt-oss-120b",
        temperature=0,
    ).with_structured_output(AnswerResponse)
    response = model.invoke(
        PROMPT.invoke(
            {
                "history": "\n".join(f"{item['role']}: {item['content']}" for item in history),
                "context": context,
                "question": question,
            }
        )
    )
    allowed_chunks = {document.metadata.get("chunk_id") for document, _ in relevant}
    response.sources = [
        source
        for source in response.sources
        if str(source.chunk_id) in allowed_chunks
    ]
    if not response.found or not response.sources:
        response = AnswerResponse(answer=NO_ANSWER, found=False, sources=[])
    save_message(
        conversation_id,
        "assistant",
        response.answer,
        [source.model_dump(mode="json") for source in response.sources],
    )
    return response
