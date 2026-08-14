from pathlib import Path

import pytest

from app.services.document_loader import load_document
from app.services.document_service import make_topic


def test_make_topic_uses_filename_without_extension() -> None:
    assert make_topic("зоопарк_правила.pdf") == "зоопарк правила"


def test_loader_rejects_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "document.doc"
    path.write_bytes(b"legacy document")

    with pytest.raises(ValueError, match="TXT, DOCX и PDF"):
        load_document(path)


def test_loader_reads_utf8_text(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("Правила зоопарка", encoding="utf-8")

    documents = load_document(path)

    assert documents[0].page_content == "Правила зоопарка"
