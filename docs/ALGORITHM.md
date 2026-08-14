# Алгоритм решения

## Индексация

1. API принимает файл и проверяет расширение.
2. LangChain loader извлекает текст и сохраняет номер страницы в metadata.
3. `RecursiveCharacterTextSplitter` создаёт чанки по 800 символов с overlap 120.
4. К чанкам добавляются `document_id`, тема, имя файла, страница и индекс.
5. Embedding-модель создаёт 384-мерный вектор для каждого чанка с префиксом `passage:`.
6. LangChain `PGVector` сохраняет текст, metadata и embedding в PostgreSQL.

## Ответ

1. API принимает вопрос и `document_id` активной вкладки.
2. Вопрос кодируется с префиксом `query:`.
3. PGVector выполняет similarity search с фильтром по `document_id`.
4. При недостаточной релевантности возвращается отказ без вызова LLM.
5. Найденные фрагменты передаются в строгий prompt Groq.
6. Groq возвращает структурированный ответ с `answer`, `found` и `sources`.
7. API проверяет источники и отдаёт JSON frontend.
