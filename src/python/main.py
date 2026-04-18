from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.dependencies import get_embedder, get_settings, get_vector_store
from .api.router import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI-TAURON Compliance API")

    # Ensure Qdrant collections exist
    settings = get_settings()
    vs = get_vector_store()
    embedder = get_embedder()
    vs.create_collection(settings.legal_acts_collection, embedder.dimension)
    vs.create_collection(settings.contracts_collection, embedder.dimension)

    logger.info("Qdrant collections ready")
    yield
    logger.info("Shutting down AI-TAURON Compliance API")


app = FastAPI(
    title="AI-TAURON Compliance API",
    version="0.1.0",
    description="Automatyczna analiza zgodności umów z przepisami prawa energetycznego",
    lifespan=lifespan,
)
app.include_router(router)
