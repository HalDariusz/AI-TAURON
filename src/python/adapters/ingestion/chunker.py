from __future__ import annotations

import logging
import re
import uuid

from ...domain.models import Chunk, ChunkMetadata, Document

logger = logging.getLogger(__name__)

# Patterns for detecting structural boundaries in Polish legal documents
_ARTICLE_RE = re.compile(r"^(Art\.\s*\d+[a-z]*\.?)", re.MULTILINE)
_PARAGRAPH_RE = re.compile(r"^(§\s*\d+\.?)", re.MULTILINE)
_USTEP_RE = re.compile(r"^(\d+\.\s)", re.MULTILINE)
_SECTION_RE = re.compile(
    r"^(Rozdział\s+[IVXLCDM\d]+|Dział\s+[IVXLCDM\d]+|CZĘŚĆ\s+[IVXLCDM\d]+)",
    re.MULTILINE | re.IGNORECASE,
)


class StructureAwareChunker:
    """Chunks legal documents by logical structure (articles, paragraphs, sections)."""

    def __init__(
        self,
        max_tokens: int = 1024,
        min_tokens: int = 128,
        overlap_context: bool = True,
    ) -> None:
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.overlap_context = overlap_context
        self._tokenizer = None

    def _get_tokenizer(self):
        if self._tokenizer is None:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(
                "sdadas/mmlw-roberta-large", use_fast=True
            )
        return self._tokenizer

    def _count_tokens(self, text: str) -> int:
        return len(self._get_tokenizer().encode(text, add_special_tokens=False))

    def chunk(self, document: Document) -> list[Chunk]:
        if not document.raw_text.strip():
            return []

        sections = self._split_into_sections(document.raw_text)
        chunks: list[Chunk] = []

        for idx, section in enumerate(sections):
            text = section["text"].strip()
            if not text:
                continue

            token_count = self._count_tokens(text)

            if token_count > self.max_tokens:
                sub_chunks = self._split_large_section(section, document)
                for sub_idx, sub in enumerate(sub_chunks):
                    chunks.append(self._make_chunk(
                        sub["text"],
                        document,
                        sub.get("hierarchy", section.get("hierarchy", [])),
                        len(chunks),
                        article=sub.get("article", section.get("article")),
                        paragraph=sub.get("paragraph", section.get("paragraph")),
                    ))
            elif token_count < self.min_tokens and sections and idx < len(sections) - 1:
                # Too small — will be merged with next section during post-processing
                chunks.append(self._make_chunk(
                    text,
                    document,
                    section.get("hierarchy", []),
                    len(chunks),
                    article=section.get("article"),
                    paragraph=section.get("paragraph"),
                ))
            else:
                chunks.append(self._make_chunk(
                    text,
                    document,
                    section.get("hierarchy", []),
                    len(chunks),
                    article=section.get("article"),
                    paragraph=section.get("paragraph"),
                ))

        chunks = self._merge_small_chunks(chunks)
        return chunks

    def _split_into_sections(self, text: str) -> list[dict]:
        """Split text into logical sections based on legal structure markers."""
        # Try article-level split first (legal acts)
        parts = self._split_by_pattern(text, _ARTICLE_RE, "article")
        if len(parts) > 1:
            return parts

        # Try paragraph-level split (contracts, OWU)
        parts = self._split_by_pattern(text, _PARAGRAPH_RE, "paragraph")
        if len(parts) > 1:
            return parts

        # Fallback: split by double newlines
        return self._split_by_newlines(text)

    def _split_by_pattern(self, text: str, pattern: re.Pattern, label: str) -> list[dict]:
        """Split text by regex pattern, preserving the matched header."""
        matches = list(pattern.finditer(text))
        if not matches:
            return [{"text": text, "hierarchy": [], label: None}]

        sections: list[dict] = []

        # Text before first match (preamble)
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections.append({"text": preamble, "hierarchy": ["Preambuła"], label: None})

        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()

            header = match.group(1).strip().rstrip(".")
            sections.append({
                "text": section_text,
                "hierarchy": [header],
                label: header,
            })

        return sections

    def _split_by_newlines(self, text: str) -> list[dict]:
        """Fallback: split by double newlines into paragraph-sized chunks."""
        paragraphs = re.split(r"\n\s*\n", text)
        return [
            {"text": p.strip(), "hierarchy": [], "article": None, "paragraph": None}
            for p in paragraphs
            if p.strip()
        ]

    def _split_large_section(self, section: dict, document: Document) -> list[dict]:
        """Split a section that exceeds max_tokens into smaller pieces."""
        text = section["text"]
        parent_hierarchy = section.get("hierarchy", [])

        # Try splitting by ustęp (numbered sub-items)
        parts = self._split_by_pattern(text, _USTEP_RE, "paragraph")
        if len(parts) > 1:
            for p in parts:
                p["hierarchy"] = parent_hierarchy + p.get("hierarchy", [])
            return parts

        # Fallback: split by sentences, respecting token limits
        return self._split_by_sentences(text, parent_hierarchy)

    def _split_by_sentences(self, text: str, hierarchy: list[str]) -> list[dict]:
        """Split text into chunks at sentence boundaries."""
        sentences = re.split(r"(?<=[.;])\s+", text)
        chunks: list[dict] = []
        current: list[str] = []
        current_tokens = 0

        for sentence in sentences:
            sent_tokens = self._count_tokens(sentence)
            if current_tokens + sent_tokens > self.max_tokens and current:
                chunks.append({
                    "text": " ".join(current),
                    "hierarchy": hierarchy,
                    "article": None,
                    "paragraph": None,
                })
                current = [sentence]
                current_tokens = sent_tokens
            else:
                current.append(sentence)
                current_tokens += sent_tokens

        if current:
            chunks.append({
                "text": " ".join(current),
                "hierarchy": hierarchy,
                "article": None,
                "paragraph": None,
            })

        return chunks

    def _merge_small_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        """Merge consecutive chunks that are below min_tokens."""
        if not chunks:
            return chunks

        merged: list[Chunk] = []
        buffer: Chunk | None = None

        for chunk in chunks:
            if buffer is None:
                buffer = chunk
                continue

            buffer_tokens = self._count_tokens(buffer.text)
            if buffer_tokens < self.min_tokens:
                # Merge with current chunk
                buffer = Chunk(
                    id=buffer.id,
                    text=buffer.text + "\n\n" + chunk.text,
                    metadata=buffer.metadata,
                    token_count=0,
                )
            else:
                buffer.token_count = buffer_tokens
                merged.append(buffer)
                buffer = chunk

        if buffer is not None:
            buffer.token_count = self._count_tokens(buffer.text)
            merged.append(buffer)

        # Re-index
        for idx, chunk in enumerate(merged):
            chunk.metadata.chunk_index = idx

        return merged

    def _make_chunk(
        self,
        text: str,
        document: Document,
        hierarchy: list[str],
        index: int,
        *,
        article: str | None = None,
        paragraph: str | None = None,
    ) -> Chunk:
        prefix = ""
        if self.overlap_context and hierarchy:
            prefix = " > ".join(hierarchy) + "\n\n"

        full_text = prefix + text if prefix else text

        return Chunk(
            id=str(uuid.uuid4()),
            text=full_text,
            metadata=ChunkMetadata(
                document_id=document.id,
                document_type=document.document_type,
                source_file=document.filename,
                section_hierarchy=hierarchy,
                article_number=article,
                paragraph_number=paragraph,
                chunk_index=index,
            ),
            token_count=self._count_tokens(full_text),
        )
