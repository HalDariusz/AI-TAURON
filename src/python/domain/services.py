from __future__ import annotations

import json
import logging
import re
import time

from .models import Chunk, ComplianceReport, Document, DocumentType, Finding, Severity
from .ports import (
    BlockchainRegistry,
    Chunker,
    DocumentParser,
    Embedder,
    ExperimentTracker,
    LLMProvider,
    VectorStore,
)

logger = logging.getLogger(__name__)


class ComplianceAnalyzer:
    def __init__(
        self,
        parser: DocumentParser,
        chunker: Chunker,
        embedder: Embedder,
        vector_store: VectorStore,
        llm: LLMProvider,
        tracker: ExperimentTracker,
        *,
        legal_collection: str = "legal_acts",
        contracts_collection: str = "contracts",
        retrieval_top_k: int = 10,
        prompt_version: str = "v1.0",
        model_name: str = "mistral",
    ):
        self._parser = parser
        self._chunker = chunker
        self._embedder = embedder
        self._vector_store = vector_store
        self._llm = llm
        self._tracker = tracker
        self._legal_collection = legal_collection
        self._contracts_collection = contracts_collection
        self._retrieval_top_k = retrieval_top_k
        self._prompt_version = prompt_version
        self._model_name = model_name
        self._compliance_prompt_template: str = ""
        self._document_prompt_template: str = ""
        self._blockchain: BlockchainRegistry | None = None

    def set_blockchain(self, blockchain: BlockchainRegistry) -> None:
        """Set the blockchain registry for report registration."""
        self._blockchain = blockchain

    def set_compliance_prompt(self, template: str) -> None:
        """Set the prompt template for clause-level compliance analysis."""
        self._compliance_prompt_template = template

    def set_document_prompt(self, template: str) -> None:
        """Set the prompt template for document-level analysis (missing sections)."""
        self._document_prompt_template = template

    def ingest_document(self, file_path: str, doc_type: DocumentType) -> Document:
        """Parse, chunk, embed and index a document."""
        document = self._parser.parse(file_path, doc_type)
        document.chunks = self._chunker.chunk(document)

        texts = [chunk.text for chunk in document.chunks]
        embeddings = self._embedder.embed(texts)

        collection = (
            self._legal_collection
            if doc_type == DocumentType.LEGAL_ACT
            else self._contracts_collection
        )
        self._vector_store.upsert(document.chunks, embeddings, collection)

        logger.info(
            "Ingested %s: %d chunks into %s", document.filename, len(document.chunks), collection
        )
        return document

    def _fetch_document_chunks(self, document: Document) -> list[dict]:
        """Fetch document chunks from Qdrant (not from PG which has no chunks)."""
        collection = (
            self._legal_collection
            if document.document_type == DocumentType.LEGAL_ACT
            else self._contracts_collection
        )

        # Search by document_id filter in Qdrant
        try:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            results = self._vector_store._client.scroll(
                collection_name=collection,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document.id),
                        )
                    ]
                ),
                limit=500,
                with_payload=True,
                with_vectors=False,
            )
            chunks = [
                {
                    "text": p.payload.get("text", ""),
                    "section": " > ".join(p.payload.get("section_hierarchy", [])),
                    "chunk_index": p.payload.get("chunk_index", 0),
                }
                for p in results[0]
            ]
            chunks.sort(key=lambda c: c["chunk_index"])
            logger.info("Fetched %d chunks for %s from Qdrant", len(chunks), document.filename)
            return chunks
        except Exception as e:
            logger.error("Failed to fetch chunks from Qdrant: %s", e)
            return []

    def analyze_document(self, document: Document) -> ComplianceReport:
        """Run compliance analysis: chunk-level + document-level."""
        if not self._compliance_prompt_template:
            raise ValueError("Compliance prompt template not set.")
        if not self._document_prompt_template:
            raise ValueError("Document prompt template not set.")

        start_time = time.time()

        run_id = self._tracker.start_run(
            run_name=f"analysis-{document.filename}",
            tags={"document": document.filename, "model": self._model_name},
        )
        self._tracker.log_params({
            "model_name": self._model_name,
            "prompt_version": self._prompt_version,
            "retrieval_top_k": str(self._retrieval_top_k),
        })

        # Fetch chunks from Qdrant (PG doesn't store them)
        chunks = self._fetch_document_chunks(document)

        if not chunks:
            logger.warning("No chunks found for %s — cannot analyze", document.filename)
            self._tracker.end_run()
            return ComplianceReport(
                document_id=document.id,
                document_name=document.filename,
                summary="Brak chunków — dokument nie został zaindeksowany.",
                model_name=self._model_name,
                prompt_version=self._prompt_version,
            )

        all_findings: list[Finding] = []

        # --- Phase 1: Chunk-level analysis (finds violations IN clauses) ---
        logger.info("Phase 1: Chunk-level analysis (%d chunks)", len(chunks))
        for i, chunk in enumerate(chunks):
            query_embedding = self._embedder.embed([chunk["text"]])[0]
            legal_results = self._vector_store.search(
                query_embedding, self._legal_collection, self._retrieval_top_k
            )

            if not legal_results:
                continue

            legal_context = "\n\n".join(r.get("text", "") for r in legal_results)

            prompt = self._compliance_prompt_template.format(
                contract_clause=chunk["text"],
                legal_context=legal_context,
            )

            logger.info("  Analyzing chunk %d/%d...", i + 1, len(chunks))
            response = self._llm.complete(prompt)
            data = self._extract_json(response)
            if data and not data.get("is_compliant", True):
                for f in data.get("findings", []):
                    try:
                        all_findings.append(Finding(
                            clause_text=f.get("clause_text", chunk["text"][:200]),
                            regulation_ref=f.get("regulation_ref", ""),
                            description=f.get("description", ""),
                            severity=Severity(f.get("severity", "medium").lower()),
                            recommendation=f.get("recommendation", ""),
                        ))
                    except (ValueError, KeyError) as e:
                        logger.warning("Failed to parse finding: %s", e)

        # --- Phase 2: Document-level analysis (finds MISSING sections) ---
        logger.info("Phase 2: Document-level analysis (missing sections)")

        # Build document structure summary (sections/paragraphs list)
        doc_structure = "\n".join(
            f"- {c['section']}: {c['text'][:120]}..."
            if c["section"]
            else f"- Chunk {c['chunk_index']}: {c['text'][:120]}..."
            for c in chunks
        )

        # Retrieve broad legal context for document-level check
        doc_query = (
            "wymagania umowy sprzedaży energii elektrycznej konsument "
            "odstąpienie wypowiedzenie reklamacja informacje przedkontraktowe"
        )
        doc_embedding = self._embedder.embed([doc_query])[0]
        legal_results = self._vector_store.search(
            doc_embedding, self._legal_collection, self._retrieval_top_k
        )
        legal_context = "\n\n".join(r.get("text", "") for r in legal_results)

        doc_type_label = {
            "contract": "umowa sprzedaży energii",
            "owu": "OWU (Ogólne Warunki Umów)",
            "legal_act": "akt prawny",
        }.get(document.document_type.value, "dokument")

        prompt = self._document_prompt_template.format(
            document_type=doc_type_label,
            document_text=doc_structure[:6000],
            legal_context=legal_context[:4000],
        )

        logger.info("  Running document-level LLM analysis...")
        response = self._llm.complete(prompt)
        data = self._extract_json(response)
        if data:
            for f in data.get("findings", []):
                try:
                    all_findings.append(Finding(
                        clause_text=f.get("clause_text", ""),
                        regulation_ref=f.get("regulation_ref", ""),
                        description=f.get("description", ""),
                        severity=Severity(f.get("severity", "medium").lower()),
                        recommendation=f.get("recommendation", ""),
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning("Failed to parse doc-level finding: %s", e)

        all_findings = self._deduplicate_findings(all_findings)

        duration = time.time() - start_time
        report = ComplianceReport(
            document_id=document.id,
            document_name=document.filename,
            findings=all_findings,
            summary=self._generate_summary(all_findings),
            model_name=self._model_name,
            prompt_version=self._prompt_version,
        )

        self._tracker.log_metrics({
            "total_findings": float(report.total_findings),
            "critical_count": float(report.critical_count),
            "high_count": float(report.high_count),
            "duration_seconds": duration,
        })
        self._tracker.end_run()

        logger.info(
            "Analysis complete for %s: %d findings in %.1fs (run_id=%s)",
            document.filename,
            report.total_findings,
            duration,
            run_id,
        )

        # Blockchain registration (non-blocking)
        self._blockchain_tx_id: str | None = None
        if self._blockchain:
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self._register_on_blockchain(report))
                else:
                    loop.run_until_complete(self._register_on_blockchain(report))
            except Exception as e:
                logger.warning("Blockchain registration skipped: %s", e)

        return report

    async def _register_on_blockchain(self, report: ComplianceReport) -> None:
        """Register report on Hyperledger Fabric (async)."""
        try:
            tx_id = await self._blockchain.register_compliance_report(report)
            self._blockchain_tx_id = tx_id
            logger.info("Blockchain TX: %s for report %s", tx_id, report.id)
        except Exception as e:
            logger.error("Blockchain registration failed for %s: %s", report.id, e)

    def _parse_llm_response(self, response: str, source_chunk: Chunk) -> list[Finding]:
        """Parse LLM JSON response into Finding objects."""
        data = self._extract_json(response)
        if not data:
            return []

        if data.get("is_compliant", True) and not data.get("findings"):
            return []

        findings = []
        for f in data.get("findings", []):
            try:
                findings.append(Finding(
                    clause_text=f.get("clause_text", source_chunk.text[:200]),
                    regulation_ref=f.get("regulation_ref", ""),
                    description=f.get("description", ""),
                    severity=Severity(f.get("severity", "medium").lower()),
                    recommendation=f.get("recommendation", ""),
                    source_chunks=[source_chunk.id],
                ))
            except (ValueError, KeyError) as e:
                logger.warning("Failed to parse finding: %s", e)
        return findings

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        """Extract JSON from LLM response, handling markdown code blocks."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from ```json ... ``` block
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding first { ... } block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Could not extract JSON from LLM response")
        return None

    @staticmethod
    def _deduplicate_findings(findings: list[Finding]) -> list[Finding]:
        """Remove duplicate findings based on regulation_ref + similar description."""
        seen: set[str] = set()
        unique: list[Finding] = []
        for f in findings:
            key = f"{f.regulation_ref}:{f.description[:80]}"
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    @staticmethod
    def _generate_summary(findings: list[Finding]) -> str:
        if not findings:
            return "Dokument jest zgodny z analizowanymi przepisami prawa."

        by_severity = {}
        for f in findings:
            by_severity.setdefault(f.severity.value, []).append(f)

        parts = [f"Wykryto {len(findings)} niezgodności."]
        for sev in ["critical", "high", "medium", "low"]:
            count = len(by_severity.get(sev, []))
            if count:
                parts.append(f"{sev.upper()}: {count}")

        return " ".join(parts)
