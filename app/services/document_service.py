from pathlib import Path
from uuid import UUID, uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.db import get_connection
from app.services.document_loader import load_document
from app.services.vector_store import add_chunks


def make_topic(filename: str) -> str:
    topic = Path(filename).stem.replace("_", " ").replace("-", " ").strip()
    return topic[:120] or "Без названия"


def index_file(filename: str, content: bytes) -> dict:
    document_id = uuid4()
    upload_dir = Path(get_settings().upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{document_id}{Path(filename).suffix.lower()}"
    path.write_bytes(content)

    loaded = load_document(path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    topic = make_topic(filename)
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
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (id, filename, topic, file_type, chunk_count)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                document_id,
                filename,
                topic,
                Path(filename).suffix.lower().lstrip("."),
                len(chunks),
            ),
        )
        connection.commit()

    return {
        "id": document_id,
        "filename": filename,
        "topic": topic,
        "file_type": Path(filename).suffix.lower().lstrip("."),
        "chunk_count": len(chunks),
    }


def list_documents() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, filename, topic, file_type, uploaded_at, chunk_count
            FROM documents
            ORDER BY uploaded_at DESC
            """
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
