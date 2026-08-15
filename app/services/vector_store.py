from functools import lru_cache
from uuid import UUID, uuid4

from langchain_postgres import PGVector

from app.config import get_settings
from app.services.embeddings import get_embeddings


def _sqlalchemy_connection_string() -> str:
    url = get_settings().database_url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@lru_cache
def get_vector_store() -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name="document_chunks",
        connection=_sqlalchemy_connection_string(),
        use_jsonb=True,
    )


def add_chunks(documents: list, document_id: UUID) -> list[str]:
    ids = [str(uuid4()) for _ in documents]
    for chunk_id, document in zip(ids, documents):
        document.metadata["chunk_id"] = chunk_id
    get_vector_store().add_documents(documents, ids=ids)
    return ids
