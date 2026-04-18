from __future__ import annotations

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ...domain.models import Chunk

logger = logging.getLogger(__name__)


class QdrantStore:
    """Vector store adapter for Qdrant."""

    def __init__(self, url: str = "http://localhost:6333") -> None:
        self._client = QdrantClient(url=url)

    def create_collection(self, collection: str, dimension: int) -> None:
        if self.collection_exists(collection):
            logger.info("Collection %s already exists", collection)
            return
        self._client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )
        logger.info("Created collection %s (dim=%d)", collection, dimension)

    def collection_exists(self, collection: str) -> bool:
        try:
            self._client.get_collection(collection)
            return True
        except Exception:
            return False

    def upsert(
        self, chunks: list[Chunk], embeddings: list[list[float]], collection: str
    ) -> None:
        points = [
            PointStruct(
                id=chunk.id,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "document_id": chunk.metadata.document_id,
                    "document_type": chunk.metadata.document_type.value,
                    "source_file": chunk.metadata.source_file,
                    "section_hierarchy": chunk.metadata.section_hierarchy,
                    "article_number": chunk.metadata.article_number,
                    "paragraph_number": chunk.metadata.paragraph_number,
                    "chunk_index": chunk.metadata.chunk_index,
                },
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]
        self._client.upsert(collection_name=collection, points=points)
        logger.info("Upserted %d points into %s", len(points), collection)

    def search(
        self,
        query_embedding: list[float],
        collection: str,
        top_k: int = 10,
    ) -> list[dict]:
        results = self._client.query_points(
            collection_name=collection,
            query=query_embedding,
            limit=top_k,
        )
        return [
            {
                "id": point.id,
                "score": point.score,
                **point.payload,
            }
            for point in results.points
        ]

    def delete_document(self, document_id: str, collection: str) -> None:
        self._client.delete(
            collection_name=collection,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
        logger.info("Deleted document %s from %s", document_id, collection)
