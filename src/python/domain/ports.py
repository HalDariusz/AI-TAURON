from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import Chunk, ComplianceReport, Document, DocumentType


@runtime_checkable
class DocumentParser(Protocol):
    def parse(self, file_path: str, doc_type: DocumentType) -> Document: ...


@runtime_checkable
class Chunker(Protocol):
    def chunk(self, document: Document) -> list[Chunk]: ...


@runtime_checkable
class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    def dimension(self) -> int: ...


@runtime_checkable
class VectorStore(Protocol):
    def create_collection(self, collection: str, dimension: int) -> None: ...

    def collection_exists(self, collection: str) -> bool: ...

    def upsert(
        self, chunks: list[Chunk], embeddings: list[list[float]], collection: str
    ) -> None: ...

    def search(
        self,
        query_embedding: list[float],
        collection: str,
        top_k: int = 10,
    ) -> list[dict]: ...

    def delete_document(self, document_id: str, collection: str) -> None: ...


@runtime_checkable
class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str: ...


@runtime_checkable
class ExperimentTracker(Protocol):
    def start_run(self, run_name: str, tags: dict[str, str] | None = None) -> str: ...

    def log_params(self, params: dict[str, str]) -> None: ...

    def log_metrics(self, metrics: dict[str, float]) -> None: ...

    def log_prompt(self, prompt_name: str, prompt_template: str, version: str) -> None: ...

    def log_artifact(self, local_path: str) -> None: ...

    def end_run(self) -> None: ...


@runtime_checkable
class BlockchainRegistry(Protocol):
    async def register_report(
        self,
        report_id: str,
        document_id: str,
        report_hash: str,
        verdict: str,
        findings_count: int,
        timestamp: str,
    ) -> str:
        """Register a compliance report on blockchain. Returns transaction ID."""
        ...

    async def verify_report(self, report_id: str, report_hash: str) -> bool:
        """Verify that a report hash matches the on-chain record."""
        ...

    async def get_record(self, report_id: str) -> dict | None:
        """Retrieve blockchain record for a report."""
        ...


@runtime_checkable
class ReportRepository(Protocol):
    async def save_document(self, document: Document) -> str: ...

    async def get_document(self, document_id: str) -> Document | None: ...

    async def list_documents(self) -> list[Document]: ...

    async def save_report(self, report: ComplianceReport) -> str: ...

    async def get_report(self, report_id: str) -> ComplianceReport | None: ...

    async def list_reports(self, skip: int = 0, limit: int = 20) -> list[ComplianceReport]: ...

    async def delete_document(self, document_id: str) -> None: ...
