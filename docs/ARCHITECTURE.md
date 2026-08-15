# Архитектура

Сервис состоит из HTML/CSS/JavaScript-клиента, FastAPI, LangChain, PostgreSQL и расширения pgvector.

```text
Browser -> FastAPI -> LangChain -> PostgreSQL/pgvector
                          |
                          -> Hugging Face Inference API для embeddings
                          -> Groq для генерации ответа
```

Каждый загруженный файл становится отдельным документом и отдельной вкладкой. Чанки документа хранятся с `document_id`, поэтому retrieval из вкладки не видит данные других документов.

## Компоненты

- `app/api` содержит HTTP endpoints.
- `app/services` содержит загрузку, разбиение, embeddings, индексацию и RAG.
- `app/schemas` содержит Pydantic-контракты API.
- `app/static` содержит frontend без отдельного JavaScript-фреймворка.
- PostgreSQL хранит метаданные документов и векторную коллекцию LangChain PGVector.

## Почему Hugging Face Inference API

Изначально embeddings считались локально через `sentence-transformers` (`intfloat/multilingual-e5-small`). Локальная модель требует ~2 ГБ RAM на torch и скачивание весов при каждом старте контейнера, поэтому на ограниченном тарифе Northflank (0.2 CPU, 512 МБ RAM) сервис не запускался — не хватало процессора и памяти.

Вынос эмбеддингов в Hugging Face Inference API решает проблему:

- модель `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` вызывается удалённо и возвращает 384-мерные векторы, идентичные по размерности локальной схеме pgvector;
- из контейнера уходит torch и `sentence-transformers`, потребление RAM падает до ~300–400 МБ;
- модель мультиязычная и хорошо работает с русским текстом;
- бесплатный read-токен `HF_TOKEN` покрывает запросы для демонстрационных нагрузок.

Ограничение: каждый запрос эмбеддинга — внешний HTTP-вызов с задержкой ~0.5–1 c, а бесплатный тариф Inference API имеет лимиты на объём запросов.

## Ограничения MVP

- Поддерживаются TXT, DOCX и PDF с текстовым слоем.
- Сканированные PDF требуют OCR и в MVP отклоняются или дают пустой текст.
- Старый бинарный DOC не входит в MVP.
