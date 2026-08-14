# RAG Document Service

Мини-сервис для загрузки текстовых документов, семантического поиска и ответов по содержимому документов.

## Стек

- Python 3.12 и FastAPI
- LangChain
- PostgreSQL + pgvector
- `intfloat/multilingual-e5-small` для локальных embeddings
- Groq для генерации ответов
- HTML/CSS/JavaScript frontend

## Локальный запуск

1. Скопировать `.env.example` в `.env` и указать новый `GROQ_API_KEY`.
2. Запустить PostgreSQL: `docker compose up -d postgres`.
3. Создать окружение: `python -m venv .venv`.
4. Активировать окружение и установить зависимости: `pip install -r requirements.txt`.
5. Запустить API: `uvicorn app.main:app --reload`.
6. Открыть `http://127.0.0.1:8000`.

При первом запуске embedding-модель загружается локально и может занять время.
