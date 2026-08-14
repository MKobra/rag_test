# Архитектура

Сервис состоит из HTML/CSS/JavaScript-клиента, FastAPI, LangChain, PostgreSQL и расширения pgvector.

```text
Browser -> FastAPI -> LangChain -> PostgreSQL/pgvector
                         |
                         -> Groq для генерации ответа
```

Каждый загруженный файл становится отдельным документом и отдельной вкладкой. Чанки документа хранятся с `document_id`, поэтому retrieval из вкладки не видит данные других документов.

## Компоненты

- `app/api` содержит HTTP endpoints.
- `app/services` содержит загрузку, разбиение, embeddings, индексацию и RAG.
- `app/schemas` содержит Pydantic-контракты API.
- `app/static` содержит frontend без отдельного JavaScript-фреймворка.
- PostgreSQL хранит метаданные документов и векторную коллекцию LangChain PGVector.

## Ограничения MVP

- Поддерживаются TXT, DOCX и PDF с текстовым слоем.
- Сканированные PDF требуют OCR и в MVP отклоняются или дают пустой текст.
- Старый бинарный DOC не входит в MVP.
