# API

Все endpoints, кроме `/api/health` и `/api/auth/*`, требуют заголовок:

```text
Authorization: Bearer <access_token>
```

## Авторизация

### `POST /api/auth/register`

Принимает email и пароль длиной 8-128 символов. Возвращает bearer-токен.

### `POST /api/auth/login`

Проверяет email и пароль и возвращает bearer-токен.

## `GET /api/health`

Проверяет, что приложение запущено.

## `GET /api/documents`

Возвращает список документов-вкладок.

## `POST /api/documents`

Принимает `multipart/form-data` с полем `file`.

## `GET /api/documents/{document_id}/conversations`

Возвращает чаты пользователя внутри документа.

## `POST /api/documents/{document_id}/conversations`

Создаёт новый чат в выбранном документе.

## `GET /api/conversations/{conversation_id}`

Возвращает историю сообщений выбранного чата.

## `POST /api/conversations/{conversation_id}/questions`

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

Каждый следующий вопрос отправляется в тот же `conversation_id`, поэтому модель получает последние сообщения этого чата.

## Ограничения

- Файл: максимум 10 МБ.
- Форматы: TXT, DOCX, PDF с текстовым слоем.
- Документы: максимум 30 на аккаунт.
- Загрузки: максимум 10 в час на аккаунт.
- Вопросы: максимум 20 в минуту на аккаунт.
- Вопрос: максимум 2000 символов.
- Retrieval: максимум 5 релевантных чанков.
- История в prompt: последние 8 сообщений.
