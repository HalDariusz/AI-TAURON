# AlICjA — AI Context Analisator

**Nazwa użytkownika:** Ciocia ALA
**Frontend:** http://95.217.89.69:8501

## Projekt
Compliance AI — automatyczna analiza umów klienckich pod kątem zgodności
z prawem energetycznym i regulacjami URE. Szczegóły w `opis-projektu.md`.

## Stack
- **Python**: LlamaIndex (RAG), MLflow (MLOps), Docling (parsing), FastAPI (API)
- **Frontend**: Streamlit — "Ciocia ALA" (6 stron: start, upload, analiza, raporty, blockchain, status)
- **Blockchain**: Hyperledger Fabric (rejestr raportów — hash + metadata on-chain)
- **Chaincode**: Go (`scripts/chaincode/compliance_registry.go`)
- **Infra**: Docker Compose — Qdrant, PostgreSQL, MLflow + HLF test-network
- **LLM**: Bielik 11B v3.0 Q4_K_M (natywny Ollama na hal, CPU inference)
- **Observability**: Langfuse (faza 2+)

## Deployment (hal — LIVE)
- **Ollama**: natywnie (nie Docker) — localhost:11434, 8 modeli
- **Qdrant + PostgreSQL + MLflow**: Docker Compose
- **HLF test-network**: 2 peery, orderer, 3 CA, chaincode deployed
- **HLF Gateway proxy**: Node.js na port 3001
- **FastAPI + Streamlit**: conda env `ai-tauron`
- **Serwer**: Ubuntu 24.04, 12 cores, 125 GB RAM, brak GPU, 933 GB dysk

## Struktura
```
src/python/
  domain/               — modele, porty (Protocol), serwisy
  adapters/
    ingestion/           — Docling parser, pdfplumber, chunker
    embedding/           — HuggingFace embedder (mmlw-roberta-large, 1024-dim)
    vectorstore/         — Qdrant adapter
    llm/                 — Ollama adapter (Bielik 11B)
    rag/                 — prompty compliance, pipeline RAG
    tracking/            — MLflow tracker
    persistence/         — PostgreSQL repo
    blockchain/          — Hyperledger Fabric adapter (REST → Gateway proxy)
  api/                   — FastAPI router, schemas, DI
  dashboard.py           — Streamlit "Ciocia ALA"
hlf/                     — Hyperledger Fabric network config + gateway proxy
scripts/                 — setup, data generation
  chaincode/             — Go chaincode (compliance-registry)
docker/                  — Dockerfiles (python, mlflow)
data/                    — dane wejściowe (gitignored)
tests/                   — pytest (unit, integration, e2e)
```

## Zasady
- **On-premise only** — żadne dane nie wychodzą na zewnątrz (RODO)
- **Blockchain** — każdy raport compliance → Hyperledger (hash + metadata)
- **MLflow** — każdy eksperyment logowany, prompty wersjonowane
- **Chunking** — structure-aware (artykuł/paragraf), nie naive tokenowy
- **Commity** — język angielski, via `/commit`
- **Sekrety** — nigdy w repo (.env w .gitignore)
- **Config** — `extra = "ignore"` w pydantic-settings (env vars Docker Compose)

## Uruchomienie (hal)
```bash
# Infra
docker compose up -d qdrant postgres mlflow
# Ollama już działa natywnie

# HLF (jeśli nie uruchomiony)
cd hlf/fabric-samples/test-network
./network.sh up createChannel -c compliancech -ca
./network.sh deployCC -ccn compliance-registry -ccp ~/prg/AI-TAURON/hlf/chaincode-go -ccl go -c compliancech
cd ~/prg/AI-TAURON/hlf/gateway-proxy && CHANNEL=compliancech node server.js &

# API
conda activate ai-tauron
cd ~/prg/AI-TAURON
uvicorn src.python.main:app --host 0.0.0.0 --port 8000

# Frontend
streamlit run src/python/dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## Serwisy
| Serwis | URL | Opis |
|--------|-----|------|
| Ciocia ALA | http://hal:8501 | Frontend Streamlit |
| FastAPI | http://hal:8000 | REST API |
| MLflow | http://hal:5000 | Experiment tracking |
| Qdrant | http://hal:6333 | Vector DB |
| Ollama | http://hal:11434 | LLM inference (Bielik 11B) |
| HLF Proxy | http://hal:3001 | Blockchain gateway |

## Dane testowe MVP
- 2 akty prawne (ISAP PDF) + 3 OWU + 5 umów (syntetyczne)
- 17 violations w ground-truth (`tests/fixtures/ground_truth/violations.jsonl`)
- 4 dokumenty zgodne (true negatives), 6 z naruszeniami
