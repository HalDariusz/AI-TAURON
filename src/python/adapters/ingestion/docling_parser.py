from __future__ import annotations

import logging
from pathlib import Path

from docling.document_converter import DocumentConverter

from ...domain.models import Document, DocumentType

logger = logging.getLogger(__name__)


class DoclingParser:
    """Primary document parser using IBM Docling."""

    def __init__(self) -> None:
        self._converter = DocumentConverter()

    def parse(self, file_path: str, doc_type: DocumentType) -> Document:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        logger.info("Parsing %s with Docling", path.name)
        result = self._converter.convert(str(path))

        raw_text = result.document.export_to_markdown()

        return Document(
            filename=path.name,
            document_type=doc_type,
            raw_text=raw_text,
        )
