from pathlib import Path
from datetime import datetime, timezone
from uuid import UUID, uuid4

from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.db import get_connection
from app.services.document_loader import load_document
from app.services.vector_store import add_chunks


def make_topic(filename: str) -> str:
    topic = Path(filename).stem.replace("_", " ").replace("-", " ").strip()
    return topic[:120] or "Без названия"


def generate_topic(filename: str, text: str) -> str:
    fallback = make_topic(filename)
    api_key = get_settings().groq_api_key
    if not api_key:
        return fallback
    try:
        model = ChatGroq(
            api_key=api_key,
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=20,
        )
        response = model.invoke(
            "Придумай короткое название темы документа на русском языке. "
            "Верни только 1-4 слова без кавычек и пояснений. "
            f"Имя файла: {filename}\nТекст:\n{text[:4000]}"
        )
        topic = str(response.content).strip().strip('"\'')
        if topic and len(topic) <= 120 and "\n" not in topic:
            return topic
    except Exception:
        pass
    return fallback


def index_file(filename: str, content: bytes, owner_id: UUID) -> dict:
    with get_connection() as connection:
        document_count = connection.execute(
            "SELECT COUNT(*) FROM documents WHERE owner_id = %s", (owner_id,)
        ).fetchone()[0]
    if document_count >= get_settings().max_documents:
        raise ValueError("Достигнут лимит документов для аккаунта")

    document_id = uuid4()
    upload_dir = Path(get_settings().upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{document_id}{Path(filename).suffix.lower()}"
    path.write_bytes(content)

    loaded = load_document(path)
    topic = generate_topic(filename, "\n".join(document.page_content for document in loaded))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(loaded)
    for index, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "document_id": str(document_id),
                "topic": topic,
                "filename": filename,
                "chunk_index": index,
            }
        )

    add_chunks(chunks, document_id)
    uploaded_at = datetime.now(timezone.utc)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (id, owner_id, filename, topic, file_type, chunk_count, uploaded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                document_id,
                owner_id,
                filename,
                topic,
                Path(filename).suffix.lower().lstrip("."),
                len(chunks),
                uploaded_at,
            ),
        )
        connection.commit()

    return {
        "id": document_id,
        "filename": filename,
        "topic": topic,
        "file_type": Path(filename).suffix.lower().lstrip("."),
        "uploaded_at": uploaded_at,
        "chunk_count": len(chunks),
    }


def delete_document(document_id: UUID, owner_id: UUID) -> None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT file_type FROM documents WHERE id = %s AND owner_id = %s",
            (document_id, owner_id),
        ).fetchone()
        if not row:
            raise ValueError("Документ не найден")
        connection.execute(
            "DELETE FROM langchain_pg_embedding WHERE cmetadata->>'document_id' = %s",
            (str(document_id),),
        )
        connection.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        connection.commit()

    file_type = row[0]
    if file_type:
        path = Path(get_settings().upload_dir) / f"{document_id}.{file_type}"
        path.unlink(missing_ok=True)


def list_documents(owner_id: UUID) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, filename, topic, file_type, uploaded_at, chunk_count
            FROM documents
            WHERE owner_id = %s
            ORDER BY uploaded_at DESC
            """,
            (owner_id,),
        ).fetchall()
    return [
        {
            "id": row[0],
            "filename": row[1],
            "topic": row[2],
            "file_type": row[3],
            "uploaded_at": row[4],
            "chunk_count": row[5],
        }
        for row in rows
    ]
