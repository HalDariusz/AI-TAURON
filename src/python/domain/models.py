from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DocumentType(StrEnum):
    LEGAL_ACT = "legal_act"
    OWU = "owu"
    CONTRACT = "contract"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ChunkMetadata(BaseModel):
    document_id: str
    document_type: DocumentType
    source_file: str
    section_hierarchy: list[str] = Field(default_factory=list)
    article_number: str | None = None
    paragraph_number: str | None = None
    effective_date: datetime | None = None
    chunk_index: int = 0


class Chunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    metadata: ChunkMetadata
    token_count: int = 0


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    document_type: DocumentType
    raw_text: str = ""
    chunks: list[Chunk] = Field(default_factory=list)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class Finding(BaseModel):
    clause_text: str
    regulation_ref: str
    description: str
    severity: Severity
    recommendation: str
    source_chunks: list[str] = Field(default_factory=list)


class ComplianceReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    document_name: str
    findings: list[Finding] = Field(default_factory=list)
    summary: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_name: str = ""
    prompt_version: str = ""

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.LOW)
