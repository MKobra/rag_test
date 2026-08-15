# RagAtlas

Мини-сервис для загрузки текстовых документов, семантического поиска и ответов по содержимому документов.

У каждого пользователя свои документы и чаты. После входа документ получает короткое название по содержимому через Groq, а исходное имя файла сохраняется под ним.

## Стек

- Python 3.12 и FastAPI
- LangChain
- PostgreSQL + pgvector
- Hugging Face Inference API (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) для embeddings
- Groq для генерации ответов
- HTML/CSS/JavaScript frontend

## Локальный запуск

1. Скопировать `.env.example` в `.env` и указать новый `GROQ_API_KEY` и `HF_TOKEN` (read-токен с huggingface.co).
2. Запустить PostgreSQL: `docker compose up -d postgres`.
3. Создать окружение: `python -m venv .venv`.
4. Активировать окружение и установить зависимости: `pip install -r requirements.txt`.
5. Запустить API: `uvicorn app.main:app --reload`.
6. Открыть `http://127.0.0.1:8000`.

При первом открытии создайте аккаунт с email и паролем. Пароли не хранятся в открытом виде: используется PBKDF2-HMAC-SHA256. Токен доступа передаётся в заголовке Bearer и хранится только в браузерном localStorage.

Embeddings создаются удалённо через Hugging Face Inference API и не потребляют локальный процессор или память.

Ограничения и API описаны в `docs/API.md`. Для production необходимо задать длинный случайный `JWT_SECRET`, заменить ключ Groq и вынести rate limiting из памяти процесса в Redis.
