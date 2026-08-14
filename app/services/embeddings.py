from functools import lru_cache

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


class E5Embeddings(Embeddings):
    """LangChain adapter that applies E5 retrieval prefixes consistently."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        model = get_embedding_model()
        vectors = model.encode(
            [f"passage: {text}" for text in texts],
            normalize_embeddings=True,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        model = get_embedding_model()
        vector = model.encode(
            f"query: {text}",
            normalize_embeddings=True,
        )
        return vector.tolist()


@lru_cache
def get_embeddings() -> E5Embeddings:
    return E5Embeddings()
