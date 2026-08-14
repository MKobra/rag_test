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
                filename TEXT NOT NULL,
                topic TEXT NOT NULL,
                file_type TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.commit()
