from __future__ import annotations

from functools import lru_cache

from ..adapters.blockchain.hyperledger_store import HyperledgerStore
from ..adapters.embedding.huggingface_embedder import HuggingFaceEmbedder
from ..adapters.ingestion.chunker import StructureAwareChunker
from ..adapters.ingestion.docling_parser import DoclingParser
from ..adapters.llm.ollama_llm import OllamaLLM
from ..adapters.persistence.postgres_repo import PostgresRepository
from ..adapters.rag.prompts import (
    COMPLIANCE_ANALYSIS_TEMPLATE,
    DOCUMENT_ANALYSIS_TEMPLATE,
    PROMPT_VERSION,
)
from ..adapters.tracking.mlflow_tracker import MLflowTracker
from ..adapters.vectorstore.qdrant_store import QdrantStore
from ..config import Settings
from ..domain.services import ComplianceAnalyzer


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_parser() -> DoclingParser:
    return DoclingParser()


@lru_cache
def get_chunker() -> StructureAwareChunker:
    s = get_settings()
    return StructureAwareChunker(
        max_tokens=s.chunk_max_tokens,
        min_tokens=s.chunk_min_tokens,
    )


@lru_cache
def get_embedder() -> HuggingFaceEmbedder:
    s = get_settings()
    return HuggingFaceEmbedder(model_name=s.embedding_model_name)


@lru_cache
def get_vector_store() -> QdrantStore:
    s = get_settings()
    return QdrantStore(url=s.qdrant_url)


@lru_cache
def get_llm() -> OllamaLLM:
    s = get_settings()
    return OllamaLLM(
        model=s.llm_model_name,
        base_url=s.ollama_url,
        request_timeout=s.llm_timeout,
        temperature=s.llm_temperature,
    )


@lru_cache
def get_tracker() -> MLflowTracker:
    s = get_settings()
    return MLflowTracker(
        tracking_uri=s.mlflow_tracking_uri,
        experiment_name=s.mlflow_experiment,
    )


@lru_cache
def get_repo() -> PostgresRepository:
    s = get_settings()
    return PostgresRepository(dsn=s.postgres_dsn)


@lru_cache
def get_blockchain() -> HyperledgerStore:
    s = get_settings()
    return HyperledgerStore(
        gateway_url=s.hlf_gateway_url,
        channel=s.hlf_channel,
        chaincode=s.hlf_chaincode,
    )


@lru_cache
def get_analyzer() -> ComplianceAnalyzer:
    s = get_settings()
    analyzer = ComplianceAnalyzer(
        parser=get_parser(),
        chunker=get_chunker(),
        embedder=get_embedder(),
        vector_store=get_vector_store(),
        llm=get_llm(),
        tracker=get_tracker(),
        legal_collection=s.legal_acts_collection,
        contracts_collection=s.contracts_collection,
        retrieval_top_k=s.retrieval_top_k,
        prompt_version=PROMPT_VERSION,
        model_name=s.llm_model_name,
    )
    analyzer.set_compliance_prompt(COMPLIANCE_ANALYSIS_TEMPLATE)
    analyzer.set_document_prompt(DOCUMENT_ANALYSIS_TEMPLATE)
    if s.hlf_enabled:
        analyzer.set_blockchain(get_blockchain())
    return analyzer
