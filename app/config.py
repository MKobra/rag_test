from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://rag:rag@localhost:5432/rag"
    groq_api_key: str = ""
    hf_token: str = ""
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    upload_dir: str = "uploads"
    retrieval_k: int = 5
    retrieval_distance_threshold: float = 0.65
    jwt_secret: str = "change-this-secret-in-production"
    access_token_expire_minutes: int = 60 * 24
    max_upload_size_bytes: int = 10 * 1024 * 1024
    max_questions_per_minute: int = 20
    max_uploads_per_hour: int = 10
    max_documents: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
