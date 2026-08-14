# API

## `GET /api/health`

Проверяет, что приложение запущено.

## `GET /api/documents`

Возвращает список документов-вкладок.

## `POST /api/documents`

Принимает `multipart/form-data` с полем `file`.

## `POST /api/documents/{document_id}/questions`

Принимает JSON:

```json
{"question": "Какие животные содержатся в зоопарке?"}
```

Возвращает:

```json
{
  "answer": "...",
  "found": true,
  "sources": [
    {"chunk_id": "...", "page": 3, "quote": "..."}
  ]
}
```
