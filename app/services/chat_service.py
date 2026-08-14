import json
from uuid import UUID, uuid4

from app.db import get_connection


def ensure_document_owner(document_id: UUID, owner_id: UUID) -> None:
    with get_connection() as connection:
        exists = connection.execute(
            "SELECT EXISTS (SELECT 1 FROM documents WHERE id = %s AND owner_id = %s)",
            (document_id, owner_id),
        ).fetchone()[0]
    if not exists:
        raise ValueError("Документ не найден")


def create_conversation(document_id: UUID, owner_id: UUID) -> dict:
    ensure_document_owner(document_id, owner_id)
    conversation_id = uuid4()
    with get_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO conversations (id, owner_id, document_id)
            VALUES (%s, %s, %s)
            RETURNING id, title, created_at
            """,
            (conversation_id, owner_id, document_id),
        ).fetchone()
        connection.commit()
    return {"id": row[0], "title": row[1], "created_at": row[2]}


def list_conversations(document_id: UUID, owner_id: UUID) -> list[dict]:
    ensure_document_owner(document_id, owner_id)
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            WHERE document_id = %s AND owner_id = %s
            ORDER BY created_at DESC
            """,
            (document_id, owner_id),
        ).fetchall()
    return [{"id": row[0], "title": row[1], "created_at": row[2]} for row in rows]


def get_conversation(conversation_id: UUID, owner_id: UUID) -> dict:
    with get_connection() as connection:
        conversation = connection.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            WHERE id = %s AND owner_id = %s
            """,
            (conversation_id, owner_id),
        ).fetchone()
        if not conversation:
            raise ValueError("Чат не найден")
        rows = connection.execute(
            """
            SELECT id, role, content, sources, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        ).fetchall()
    return {
        "id": conversation[0],
        "title": conversation[1],
        "created_at": conversation[2],
        "messages": [
            {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "sources": row[3],
                "created_at": row[4],
            }
            for row in rows
        ],
    }


def conversation_document(conversation_id: UUID, owner_id: UUID) -> UUID:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT document_id FROM conversations WHERE id = %s AND owner_id = %s",
            (conversation_id, owner_id),
        ).fetchone()
    if not row:
        raise ValueError("Чат не найден")
    return row[0]


def recent_messages(conversation_id: UUID, owner_id: UUID, limit: int = 8) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT m.role, m.content
            FROM messages m
            JOIN conversations c ON c.id = m.conversation_id
            WHERE m.conversation_id = %s AND c.owner_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s
            """,
            (conversation_id, owner_id, limit),
        ).fetchall()
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]


def save_message(conversation_id: UUID, role: str, content: str, sources: list[dict]) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO messages (id, conversation_id, role, content, sources) VALUES (%s, %s, %s, %s, %s::jsonb)",
            (uuid4(), conversation_id, role, content, json.dumps(sources)),
        )
        if role == "user":
            connection.execute(
                "UPDATE conversations SET title = LEFT(%s, 48) WHERE id = %s AND title = 'Новый чат'",
                (content, conversation_id),
            )
        connection.commit()
