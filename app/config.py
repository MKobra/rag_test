from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://rag:rag@localhost:5432/rag"
    groq_api_key: str = ""
    embedding_model: str = "intfloat/multilingual-e5-small"
    upload_dir: str = "uploads"
    retrieval_k: int = 5
    retrieval_distance_threshold: float = 0.65

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
