from __future__ import annotations

import logging
from pathlib import Path

import pdfplumber

from ...domain.models import Document, DocumentType

logger = logging.getLogger(__name__)


class PdfPlumberParser:
    """Fallback PDF parser using pdfplumber."""

    def parse(self, file_path: str, doc_type: DocumentType) -> Document:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        logger.info("Parsing %s with pdfplumber (fallback)", path.name)

        pages_text: list[str] = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)

        raw_text = "\n\n".join(pages_text)

        return Document(
            filename=path.name,
            document_type=doc_type,
            raw_text=raw_text,
        )
