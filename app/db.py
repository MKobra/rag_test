from contextlib import contextmanager
from typing import Iterator

import psycopg

from app.config import get_settings


def database_connection_string() -> str:
    return get_settings().database_url


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    connection_string = database_connection_string().replace(
        "postgresql+psycopg://", "postgresql://"
    )
    with psycopg.connect(connection_string) as connection:
        yield connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                owner_id UUID,
                filename TEXT NOT NULL,
                topic TEXT NOT NULL,
                file_type TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.execute(
            "ALTER TABLE documents ADD COLUMN IF NOT EXISTS owner_id UUID"
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id UUID PRIMARY KEY,
                owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                title TEXT NOT NULL DEFAULT 'Новый чат',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id UUID PRIMARY KEY,
                conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources JSONB NOT NULL DEFAULT '[]'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS documents_owner_idx ON documents(owner_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS conversations_owner_document_idx ON conversations(owner_id, document_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS messages_conversation_idx ON messages(conversation_id, created_at)")
        connection.commit()
