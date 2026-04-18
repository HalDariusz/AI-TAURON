from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DocumentListItem(BaseModel):
    id: str
    filename: str
    document_type: str
    uploaded_at: datetime
    chunk_count: int = 0


class DocumentPreview(BaseModel):
    id: str
    filename: str
    document_type: str
    uploaded_at: datetime
    chunk_count: int = 0
    chunks_preview: list[dict] = []


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    message: str


class AnalysisRequest(BaseModel):
    document_id: str


class AnalysisResponse(BaseModel):
    report_id: str
    document_id: str
    total_findings: int
    critical_count: int
    high_count: int
    blockchain_tx_id: str | None = None


class FindingResponse(BaseModel):
    clause_text: str
    regulation_ref: str
    description: str
    severity: str
    recommendation: str


class ReportResponse(BaseModel):
    id: str
    document_id: str
    document_name: str
    findings: list[FindingResponse]
    summary: str
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    model_name: str
    prompt_version: str
    created_at: datetime


class ReportListItem(BaseModel):
    id: str
    document_name: str
    total_findings: int
    critical_count: int
    high_count: int
    created_at: datetime


class BlockchainVerifyRequest(BaseModel):
    report_id: str


class BlockchainVerifyResponse(BaseModel):
    report_id: str
    verified: bool
    on_chain_hash: str | None = None
    computed_hash: str | None = None
    blockchain_record: dict | None = None


class HealthResponse(BaseModel):
    status: str
    qdrant: bool
    ollama: bool
    postgres: bool
    blockchain: bool = False
