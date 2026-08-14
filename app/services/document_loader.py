from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document


SUPPORTED_EXTENSIONS = {".txt", ".docx", ".pdf"}


def load_document(path: Path) -> list[Document]:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Поддерживаются только файлы TXT, DOCX и PDF")

    if extension == ".txt":
        loader = TextLoader(str(path), encoding="utf-8")
    elif extension == ".docx":
        loader = Docx2txtLoader(str(path))
    else:
        loader = PyPDFLoader(str(path))

    documents = loader.load()
    if not any(document.page_content.strip() for document in documents):
        raise ValueError("В документе не найден текстовый слой")
    return documents
