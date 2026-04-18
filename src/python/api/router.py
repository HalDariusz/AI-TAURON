from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..adapters.blockchain.hyperledger_store import compute_report_hash
from ..domain.models import DocumentType
from .dependencies import get_analyzer, get_blockchain, get_repo, get_settings, get_vector_store
from .schemas import (
    AnalysisRequest,
    AnalysisResponse,
    BlockchainVerifyRequest,
    BlockchainVerifyResponse,
    DocumentListItem,
    DocumentPreview,
    HealthResponse,
    ReportListItem,
    ReportResponse,
    UploadResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    vs = get_vector_store()
    settings = get_settings()

    qdrant_ok = False
    try:
        qdrant_ok = vs.collection_exists("legal_acts") or True
    except Exception:
        pass

    ollama_ok = False
    try:
        import httpx as _httpx

        r = _httpx.get(f"{settings.ollama_url}/api/tags", timeout=5.0)
        ollama_ok = r.status_code == 200
    except Exception:
        pass

    pg_ok = False
    try:
        repo = get_repo()
        await repo.initialize()
        await repo.close()
        pg_ok = True
    except Exception:
        pass

    hlf_ok = False
    if settings.hlf_enabled:
        try:
            import httpx as _httpx

            r = _httpx.get(
                f"{settings.hlf_gateway_url}/api/health", timeout=5.0
            )
            hlf_ok = r.status_code == 200
        except Exception:
            pass

    return HealthResponse(
        status="ok",
        qdrant=qdrant_ok,
        ollama=ollama_ok,
        postgres=pg_ok,
        blockchain=hlf_ok,
    )


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    try:
        doc_type = DocumentType(document_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document_type. Must be one of: {[e.value for e in DocumentType]}",
        )

    # Save uploaded file to temp location
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        analyzer = get_analyzer()
        document = analyzer.ingest_document(tmp_path, doc_type)
        document.filename = file.filename  # preserve original name

        repo = get_repo()
        await repo.initialize()
        await repo.save_document(document)
        await repo.close()

        return UploadResponse(
            document_id=document.id,
            filename=file.filename,
            chunk_count=len(document.chunks),
            message=f"Document ingested: {len(document.chunks)} chunks indexed",
        )
    except Exception as e:
        logger.exception("Failed to ingest document: %s", file.filename)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/documents", response_model=list[DocumentListItem])
async def list_documents():
    repo = get_repo()
    await repo.initialize()
    docs = await repo.list_documents()
    await repo.close()

    return [
        DocumentListItem(
            id=d.id,
            filename=d.filename,
            document_type=d.document_type.value,
            uploaded_at=d.uploaded_at,
            chunk_count=len(d.chunks),
        )
        for d in docs
    ]


@router.get("/documents/{document_id}/preview", response_model=DocumentPreview)
async def preview_document(document_id: str, max_chunks: int = 5):
    repo = get_repo()
    await repo.initialize()
    doc = await repo.get_document(document_id)
    await repo.close()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Fetch chunks from Qdrant
    vs = get_vector_store()
    settings = get_settings()
    collection = (
        settings.legal_acts_collection
        if doc.document_type.value == "legal_act"
        else settings.contracts_collection
    )

    chunks_preview = []
    try:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        results = vs._client.scroll(
            collection_name=collection,
            scroll_filter=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
            limit=max_chunks,
            with_payload=True,
        )
        for point in results[0]:
            chunks_preview.append({
                "chunk_index": point.payload.get("chunk_index", 0),
                "text": point.payload.get("text", "")[:500],
                "section": " > ".join(point.payload.get("section_hierarchy", [])),
                "article": point.payload.get("article_number"),
                "paragraph": point.payload.get("paragraph_number"),
            })
        chunks_preview.sort(key=lambda c: c["chunk_index"])
    except Exception as e:
        logger.warning("Could not fetch chunks preview: %s", e)

    return DocumentPreview(
        id=doc.id,
        filename=doc.filename,
        document_type=doc.document_type.value,
        uploaded_at=doc.uploaded_at,
        chunk_count=len(chunks_preview),
        chunks_preview=chunks_preview,
    )


@router.post("/analysis/run", response_model=AnalysisResponse)
async def run_analysis(request: AnalysisRequest):
    repo = get_repo()
    await repo.initialize()

    document = await repo.get_document(request.document_id)
    if not document:
        await repo.close()
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        analyzer = get_analyzer()
        report = analyzer.analyze_document(document)

        await repo.save_report(report)
        await repo.close()

        return AnalysisResponse(
            report_id=report.id,
            document_id=report.document_id,
            total_findings=report.total_findings,
            critical_count=report.critical_count,
            high_count=report.high_count,
        )
    except Exception as e:
        await repo.close()
        logger.exception("Analysis failed for document: %s", request.document_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", response_model=list[ReportListItem])
async def list_reports(skip: int = 0, limit: int = 20):
    repo = get_repo()
    await repo.initialize()
    reports = await repo.list_reports(skip=skip, limit=limit)
    await repo.close()

    return [
        ReportListItem(
            id=r.id,
            document_name=r.document_name,
            total_findings=r.total_findings,
            critical_count=r.critical_count,
            high_count=r.high_count,
            created_at=r.created_at,
        )
        for r in reports
    ]


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    repo = get_repo()
    await repo.initialize()
    report = await repo.get_report(report_id)
    await repo.close()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportResponse(
        id=report.id,
        document_id=report.document_id,
        document_name=report.document_name,
        findings=[
            {
                "clause_text": f.clause_text,
                "regulation_ref": f.regulation_ref,
                "description": f.description,
                "severity": f.severity.value,
                "recommendation": f.recommendation,
            }
            for f in report.findings
        ],
        summary=report.summary,
        total_findings=report.total_findings,
        critical_count=report.critical_count,
        high_count=report.high_count,
        medium_count=report.medium_count,
        low_count=report.low_count,
        model_name=report.model_name,
        prompt_version=report.prompt_version,
        created_at=report.created_at,
    )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    repo = get_repo()
    await repo.initialize()

    document = await repo.get_document(document_id)
    if not document:
        await repo.close()
        raise HTTPException(status_code=404, detail="Document not found")

    vs = get_vector_store()
    vs.delete_document(document_id, "legal_acts")
    vs.delete_document(document_id, "contracts")

    await repo.delete_document(document_id)
    await repo.close()

    return {"message": f"Document {document_id} deleted"}


@router.post("/blockchain/verify", response_model=BlockchainVerifyResponse)
async def verify_report_blockchain(request: BlockchainVerifyRequest):
    """Verify a compliance report against its blockchain record."""
    settings = get_settings()
    if not settings.hlf_enabled:
        raise HTTPException(status_code=503, detail="Blockchain not enabled")

    repo = get_repo()
    await repo.initialize()
    report = await repo.get_report(request.report_id)
    await repo.close()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    computed_hash = compute_report_hash(report)
    blockchain = get_blockchain()
    record = await blockchain.get_record(request.report_id)

    if not record:
        return BlockchainVerifyResponse(
            report_id=request.report_id,
            verified=False,
            computed_hash=computed_hash,
        )

    on_chain_hash = record.get("reportHash", "")
    return BlockchainVerifyResponse(
        report_id=request.report_id,
        verified=computed_hash == on_chain_hash,
        on_chain_hash=on_chain_hash,
        computed_hash=computed_hash,
        blockchain_record=record,
    )
