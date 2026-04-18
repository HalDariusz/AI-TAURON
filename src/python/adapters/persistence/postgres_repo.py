from __future__ import annotations

import json
import logging

import asyncpg

from ...domain.models import ComplianceReport, Document, DocumentType, Finding, Severity

logger = logging.getLogger(__name__)

INIT_SQL = """\
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    document_type TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    chunk_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    document_name TEXT NOT NULL,
    findings_json JSONB NOT NULL DEFAULT '[]',
    summary TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


class PostgresRepository:
    """Report and document metadata repository backed by PostgreSQL."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._pool: asyncpg.Pool | None = None
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized and self._pool and not self._pool._closed:
            return
        self._pool = await asyncpg.create_pool(self._dsn, min_size=2, max_size=10)
        async with self._pool.acquire() as conn:
            await conn.execute(INIT_SQL)
        self._initialized = True
        logger.info("PostgreSQL repository initialized")

    async def close(self) -> None:
        pass  # Singleton — pool lives for the app lifetime

    async def save_document(self, document: Document) -> str:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO documents (id, filename, document_type, uploaded_at, chunk_count) "
                "VALUES ($1, $2, $3, $4, $5) "
                "ON CONFLICT (id) DO UPDATE SET chunk_count = $5",
                document.id,
                document.filename,
                document.document_type.value,
                document.uploaded_at,
                len(document.chunks),
            )
        return document.id

    async def get_document(self, document_id: str) -> Document | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", document_id)
        if not row:
            return None
        return Document(
            id=row["id"],
            filename=row["filename"],
            document_type=DocumentType(row["document_type"]),
            uploaded_at=row["uploaded_at"],
        )

    async def list_documents(self) -> list[Document]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM documents ORDER BY uploaded_at DESC")
        return [
            Document(
                id=row["id"],
                filename=row["filename"],
                document_type=DocumentType(row["document_type"]),
                uploaded_at=row["uploaded_at"],
            )
            for row in rows
        ]

    async def save_report(self, report: ComplianceReport) -> str:
        findings_json = json.dumps(
            [f.model_dump() for f in report.findings], ensure_ascii=False
        )
        async with self._pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO reports "
                "(id, document_id, document_name, findings_json, summary, "
                "model_name, prompt_version, created_at) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                report.id,
                report.document_id,
                report.document_name,
                findings_json,
                report.summary,
                report.model_name,
                report.prompt_version,
                report.created_at,
            )
        return report.id

    async def get_report(self, report_id: str) -> ComplianceReport | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM reports WHERE id = $1", report_id)
        if not row:
            return None
        return self._row_to_report(row)

    async def list_reports(self, skip: int = 0, limit: int = 20) -> list[ComplianceReport]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM reports ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                limit,
                skip,
            )
        return [self._row_to_report(row) for row in rows]

    async def delete_document(self, document_id: str) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute("DELETE FROM documents WHERE id = $1", document_id)

    @staticmethod
    def _row_to_report(row: asyncpg.Record) -> ComplianceReport:
        findings_data = json.loads(row["findings_json"]) if row["findings_json"] else []
        findings = [
            Finding(
                clause_text=f["clause_text"],
                regulation_ref=f["regulation_ref"],
                description=f["description"],
                severity=Severity(f["severity"]),
                recommendation=f["recommendation"],
                source_chunks=f.get("source_chunks", []),
            )
            for f in findings_data
        ]
        return ComplianceReport(
            id=row["id"],
            document_id=row["document_id"],
            document_name=row["document_name"],
            findings=findings,
            summary=row["summary"],
            model_name=row["model_name"],
            prompt_version=row["prompt_version"],
            created_at=row["created_at"],
        )
