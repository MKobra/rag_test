# API

## `GET /health`

Проверяет, что приложение запущено.

## `GET /documents`

Возвращает список документов-вкладок.

## `POST /documents`

Принимает `multipart/form-data` с полем `file`.

## `POST /documents/{document_id}/questions`

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
