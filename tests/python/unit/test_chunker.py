"""Tests for structure-aware chunker on Polish legal documents."""

from src.adapters.ingestion.chunker import StructureAwareChunker
from src.domain.models import Document, DocumentType


def test_chunker_splits_legal_act_by_articles(sample_legal_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10)
    chunks = chunker.chunk(sample_legal_document)

    assert len(chunks) > 1, "Should split legal act into multiple chunks"

    # Check that articles are detected
    article_chunks = [c for c in chunks if c.metadata.article_number]
    assert len(article_chunks) > 0, "Should detect article numbers"

    # Check that Art. 4j is a chunk
    art4j = [c for c in chunks if c.metadata.article_number and "4j" in c.metadata.article_number]
    assert len(art4j) > 0, "Should detect Art. 4j"


def test_chunker_splits_contract_by_paragraphs(sample_contract_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10)
    chunks = chunker.chunk(sample_contract_document)

    assert len(chunks) > 1, "Should split contract into multiple chunks"

    # Check that paragraphs (§) are detected
    paragraph_chunks = [c for c in chunks if c.metadata.paragraph_number]
    assert len(paragraph_chunks) > 0, "Should detect § paragraph numbers"


def test_chunker_preserves_hierarchy(sample_legal_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10)
    chunks = chunker.chunk(sample_legal_document)

    # At least some chunks should have hierarchy metadata
    with_hierarchy = [c for c in chunks if c.metadata.section_hierarchy]
    assert len(with_hierarchy) > 0, "Should preserve section hierarchy"


def test_chunker_adds_context_prefix(sample_legal_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10, overlap_context=True)
    chunks = chunker.chunk(sample_legal_document)

    # Chunks with hierarchy should have prefix in text
    for chunk in chunks:
        if chunk.metadata.section_hierarchy:
            hierarchy_str = " > ".join(chunk.metadata.section_hierarchy)
            assert hierarchy_str in chunk.text, (
                f"Chunk should contain hierarchy prefix: {hierarchy_str}"
            )


def test_chunker_no_context_prefix_when_disabled(sample_contract_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10, overlap_context=False)
    chunks = chunker.chunk(sample_contract_document)

    for chunk in chunks:
        if chunk.metadata.section_hierarchy:
            # Text should not start with hierarchy prefix
            assert not chunk.text.startswith(" > ".join(chunk.metadata.section_hierarchy))


def test_chunker_token_count_set(sample_legal_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10)
    chunks = chunker.chunk(sample_legal_document)

    for chunk in chunks:
        assert chunk.token_count > 0, "Token count should be positive"


def test_chunker_merges_small_chunks():
    short_text = "Art. 1. A.\n\nArt. 2. B.\n\nArt. 3. C."
    doc = Document(
        filename="short.pdf",
        document_type=DocumentType.LEGAL_ACT,
        raw_text=short_text,
    )
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=500)
    chunks = chunker.chunk(doc)

    # Very short articles should be merged
    assert len(chunks) < 3, "Very short chunks should be merged"


def test_chunker_empty_document():
    doc = Document(
        filename="empty.pdf",
        document_type=DocumentType.LEGAL_ACT,
        raw_text="",
    )
    chunker = StructureAwareChunker()
    chunks = chunker.chunk(doc)

    assert chunks == [], "Empty document should produce no chunks"


def test_chunker_metadata_has_document_id(sample_legal_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10)
    chunks = chunker.chunk(sample_legal_document)

    for chunk in chunks:
        assert chunk.metadata.document_id == sample_legal_document.id
        assert chunk.metadata.source_file == "prawo_energetyczne.pdf"
        assert chunk.metadata.document_type == DocumentType.LEGAL_ACT


def test_chunker_sequential_indices(sample_legal_document):
    chunker = StructureAwareChunker(max_tokens=2048, min_tokens=10)
    chunks = chunker.chunk(sample_legal_document)

    indices = [c.metadata.chunk_index for c in chunks]
    assert indices == list(range(len(chunks))), "Chunk indices should be sequential"
