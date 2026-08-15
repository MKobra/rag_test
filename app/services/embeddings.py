from functools import lru_cache

from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings

from app.config import get_settings


@lru_cache
def get_embeddings() -> HuggingFaceEndpointEmbeddings:
    return HuggingFaceEndpointEmbeddings(
        model=get_settings().embedding_model,
        huggingfacehub_api_token=get_settings().hf_token,
    )
