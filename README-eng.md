# 👩‍⚖️ AlICjA — AI Context Analisator

**"Ciocia ALA"** — AI compliance assistant for automated analysis of energy contracts
against Polish law regulations, consumer protection acts, and URE (Energy Regulatory Office) requirements.

## Project Overview

AlICjA analyzes documents (energy sale contracts, General Terms & Conditions, comprehensive contracts)
by comparing their clauses against applicable law. The system detects non-compliance issues,
assesses their severity, and generates remediation recommendations — before they become
regulatory risks or grounds for customer complaints.

### Key Features

- **RAG Pipeline** — LlamaIndex with hierarchical retrieval (article → section → chunk)
- **Polish LLM** — Bielik 11B via Ollama, natively trained on Polish legal texts
- **Audit Trail** — Hyperledger Fabric integration, every report registered on-chain (SHA-256 hash)
- **On-Premise Deployment** — no data leaves the infrastructure (GDPR compliant)
- **Experiment Tracking** — MLflow for prompt versioning, metrics, and quality evaluation
- **Structure-Aware Document Processing** — respects legal document hierarchy (Docling + hierarchical chunking)

### Technology Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| **LLM** | Ollama + Bielik 11B (CPU inference) | ✅ Implemented |
| **RAG** | LlamaIndex + mmlw-roberta-large embeddings (1024-dim) | ✅ Implemented |
| **Vector DB** | Qdrant v1.13.2 | ✅ Implemented |
| **Database** | PostgreSQL 17 | ✅ Implemented |
| **Blockchain** | Hyperledger Fabric 2.5+ (Go chaincode) | ✅ Implemented |
| **API** | FastAPI + uvicorn | ✅ Implemented |
| **Frontend** | Streamlit ("Ciocia ALA") | ✅ Implemented |
| **Experiment Tracking** | MLflow | ✅ Implemented |
| **Document Parsing** | Docling + pdfplumber | ✅ Implemented |
| **Observability** | Langfuse (optional, phase 2+) | 🔄 Planned |
| **Infrastructure** | Docker Compose | ✅ Implemented |

## Installation & Setup

### Quick Start (Docker Compose)

```bash
git clone https://github.com/HalDariusz/AI-TAURON.git
cd AI-TAURON

# 1. Copy and configure environment
cp .env.example .env
# Edit .env — set passwords, model parameters if needed

# 2. Install Python dependencies
pip install -e ".[dev,ui]"  # or: pip install -e ".[dev]" for API only

# 3. Start all services
docker compose up -d

# 4. Verify services are healthy
docker compose ps
```

Services start in order: PostgreSQL → Qdrant → Ollama → MLflow → API → Streamlit

### Detailed Setup

#### 1. Environment Configuration

```bash
cp .env.example .env
```

Key variables in `.env`:
- `OLLAMA_MODEL` — LLM to use (default: `bielik-11b-v3.0-instruct:Q4_K_M`)
- `QDRANT_URL` — Vector DB endpoint (default: `http://qdrant:6333`)
- `POSTGRES_*` — Database credentials
- `API_BASE_URL` — API endpoint for Streamlit (default: `http://localhost:8000/api/v1`)

#### 2. Start Services

**Option A: Docker Compose (Recommended)**

```bash
# Start all services (API + databases)
docker compose up -d

# Start with UI dashboard
docker compose --profile ui up -d

# Check status
docker compose ps

# View logs
docker compose logs -f api        # Follow API logs
docker compose logs qdrant        # Vector DB logs
```

**Option B: Manual (for development)**

```bash
# Terminal 1: Qdrant
docker run -p 6333:6333 qdrant/qdrant:v1.13.2

# Terminal 2: PostgreSQL
docker run -p 5432:5432 -e POSTGRES_PASSWORD=changeme postgres:17

# Terminal 3: Ollama (must be running on host)
ollama serve

# Terminal 4: API
conda create -n ai-tauron python=3.11
conda activate ai-tauron
pip install -e ".[dev]"
uvicorn src.python.main:app --host 0.0.0.0 --port 8000

# Terminal 5: Dashboard (optional)
pip install -e ".[ui]"
streamlit run src/python/dashboard.py --server.port 8501
```

#### 3. Hyperledger Fabric Setup (Optional, for audit trail)

```bash
cd hlf
bash setup-fabric.sh init          # Download fabric-samples, binaries, start network
bash setup-fabric.sh deploycc      # Deploy compliance chaincode
bash setup-fabric.sh stop          # Stop network

# Verify chaincode is deployed
peer chaincode query -C compliancech -n compliance-registry -c '{"function":"invoke","Args":["hello"]}'
```

**Note:** The HLF integration is optional. The API works fully without blockchain — reports are stored in PostgreSQL regardless. When HLF is available, report hashes are additionally recorded on-chain for audit purposes.

## Usage — Happy Path

### 1. Access the Dashboard

Navigate to **http://localhost:8501** — you'll see the Streamlit dashboard ("Ciocia ALA").

### 2. Add Legal Acts (Knowledge Base)

First, populate the system with the legal knowledge base — these are the documents contracts will be checked against.

1. Sidebar → **📤 Add Document**
2. Select type: **📜 Legal Act**
3. Upload PDF (e.g., Energy Law, Consumer Protection Act)
4. Click **Upload and Index**
5. Docling parses the document → hierarchical chunking → embedded in Qdrant
6. Repeat for each legal act

### 3. Upload a Contract for Analysis

1. Sidebar → **📤 Add Document**
2. Select type: **📄 Contract** or **📋 General Terms**
3. Upload file (PDF/DOCX/TXT)
4. Click **Upload and Index**
5. Note the **Document ID** displayed

### 4. Run Compliance Analysis

1. Sidebar → **🔍 Analysis**
2. Select a contract from the dropdown (or paste Document ID)
3. Preview pane shows document structure (clauses/sections)
4. Click **Run Compliance Check**
5. LlamaIndex retrieves relevant legal articles → LLM analyzes each clause → generates report
6. Results displayed:
   - **Findings** — list of non-compliance issues
   - **Severity** — critical/high/medium/low (color-coded)
   - **Remediation** — recommendations for each violation
   - **Metadata** — LLM model version, prompt version, execution time

### 5. Browse & Compare Reports

1. Sidebar → **📊 Reports**
2. List of all analysis reports with severity indicators
3. Click a report → detailed view:
   - Summary statistics
   - Full violation list with references to violated regulations
   - LLM and prompt versions used
   - Timestamp and execution metadata

### 6. Verify Report Integrity (Optional)

If Hyperledger Fabric is configured:

1. Sidebar → **🔗 Blockchain**
2. Select a report or paste Report ID
3. Click **Verify Integrity**
4. System compares SHA-256 hash with on-chain record:
   - ✅ **Verified** — report unchanged since analysis
   - ❌ **Tampered** — report was modified after analysis

### 7. Monitor & Debug

1. Sidebar → **📊 MLflow Dashboard** (link to http://localhost:5000)
   - View experiment runs
   - Compare prompt versions
   - Track metrics (precision, recall, execution time)
2. Sidebar → **🔍 API Docs** (link to http://localhost:8000/docs)
   - Interactive Swagger documentation

## API Reference

### Health & Status

```
GET /api/v1/health
```
Returns status of all services (API, Qdrant, PostgreSQL, Ollama, HLF).

### Document Management

```
GET /api/v1/documents
GET /api/v1/documents?type=contract&limit=10
GET /api/v1/documents/{id}
GET /api/v1/documents/{id}/preview
POST /api/v1/documents/upload
DELETE /api/v1/documents/{id}
```

**POST /api/v1/documents/upload** — Upload and index a document

Request body (multipart/form-data):
```json
{
  "file": <binary>,
  "type": "legal_act|contract|terms",
  "title": "string",
  "metadata": {"key": "value"}
}
```

Response:
```json
{
  "id": "doc-12345",
  "title": "Energy Law",
  "type": "legal_act",
  "pages": 47,
  "chunks": 312,
  "status": "indexed",
  "indexed_at": "2026-05-01T09:00:00Z"
}
```

### Compliance Analysis

```
POST /api/v1/analysis/run
GET /api/v1/analysis/run/{run_id}
```

**POST /api/v1/analysis/run** — Run compliance analysis on a contract

Request body:
```json
{
  "document_id": "doc-12345",
  "legal_acts": ["doc-legal-1", "doc-legal-2"],
  "include_blockchain": true,
  "mlflow_experiment_id": "exp-123"
}
```

Response:
```json
{
  "run_id": "run-abc123",
  "document_id": "doc-12345",
  "status": "queued|running|completed|failed",
  "progress": 45,
  "created_at": "2026-05-01T09:00:00Z",
  "started_at": "2026-05-01T09:01:00Z",
  "completed_at": null
}
```

### Reports

```
GET /api/v1/reports
GET /api/v1/reports?status=completed&severity=critical
GET /api/v1/reports/{id}
DELETE /api/v1/reports/{id}
```

**GET /api/v1/reports/{id}** — Full report details

Response:
```json
{
  "id": "rep-xyz789",
  "document_id": "doc-12345",
  "analysis_run_id": "run-abc123",
  "status": "completed",
  "summary": {
    "total_clauses": 42,
    "findings_count": 5,
    "severity_distribution": {
      "critical": 1,
      "high": 2,
      "medium": 2,
      "low": 0
    }
  },
  "findings": [
    {
      "id": "find-001",
      "clause_excerpt": "Dostawca uprawniony jest do...",
      "violated_regulation": "Art. 23 ust. 1 Ustawy o ochronie...",
      "severity": "high",
      "description": "Klauzula umożliwia jednostronne...",
      "recommendation": "Zmienić na: 'Zmiana warunków wymaga...",
      "confidence": 0.92
    }
  ],
  "metadata": {
    "llm_model": "bielik-11b-v3.0-instruct:Q4_K_M",
    "prompt_version": "v2.3",
    "mlflow_run_id": "run-mlflow-123",
    "execution_time_seconds": 127.5,
    "tokens_used": 4521
  },
  "created_at": "2026-05-01T09:15:00Z",
  "blockchain_hash": "0x3a4b5c...",
  "blockchain_verified": true
}
```

### Blockchain Verification (Optional)

```
POST /api/v1/blockchain/verify
GET /api/v1/blockchain/reports/{id}
```

**POST /api/v1/blockchain/verify** — Verify report integrity on Hyperledger Fabric

Request body:
```json
{
  "report_id": "rep-xyz789"
}
```

Response:
```json
{
  "report_id": "rep-xyz789",
  "verified": true,
  "on_chain_hash": "0x3a4b5c...",
  "current_hash": "0x3a4b5c...",
  "block_timestamp": "2026-05-01T09:16:00Z",
  "transaction_id": "tx-hlf-12345"
}
```

### Full API Documentation

Interactive Swagger UI: **http://localhost:8000/docs**

## Architecture
## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│          👩‍⚖️ Ciocia ALA (Streamlit Frontend)             │
│                    :8501                                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP (HTTPS in prod)
┌────────────────────────▼────────────────────────────────────┐
│              FastAPI REST API Server                        │
│                    :8000                                   │
│  • Document ingestion                                       │
│  • RAG pipeline orchestration                              │
│  • Report generation & storage                             │
│  • MLflow integration                                      │
└─┬──┬────┬──────┬───────┬──────────────────────────────────┘
  │  │    │      │       │
  │  │    │      │       └────────────┐
  │  │    │      │                    │
  ▼  ▼    ▼      ▼                    ▼
┌────────┐  ┌─────────┐  ┌──────────┐  ┌────────────────┐  ┌────────┐
│ Qdrant │  │PostgreSQL│ │  Ollama  │  │     Docling    │  │ MLflow │
│:6333   │  │ :5432   │  │ :11434   │  │   (parser)     │  │ :5000  │
│Vector  │  │Metadata,│  │  Bielik  │  │  + Chunker     │  │ Track  │
│ DB     │  │ Reports │  │  11B LLM │  │                │  │ Exper. │
└────────┘  └─────────┘  └──────────┘  └────────────────┘  └────────┘
  │ RAG       │ Store    │ Inference
  │ Context   │ Results
  └───┬───────┴──────────┘
      │ (internal communication)
      │
┌─────▼─────────────────────────────────────────────────────┐
│        Hyperledger Fabric Network (Optional)              │
│              Compliance Registry Chaincode                │
│  • Report hash registration                               │
│  • Audit trail (immutable)                                │
│  • Verification queries                                   │
└────────────────────────────────────────────────────────────┘
```

### Processing Pipeline (Document Ingestion)

```
User Upload (PDF/DOCX)
        │
        ▼
┌───────────────────────┐
│  Docling Parser       │ Extracts text, structure, metadata
│  + pdfplumber         │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────────────────┐
│  Structure-Aware Hierarchical     │ Respects legal document structure:
│  Chunking                         │ • Legal act → articles → paragraphs
│  (LlamaIndex)                     │ • Contract → sections → clauses
└───────────┬───────────────────────┘
            │
            ▼
┌───────────────────────────────────┐
│  HuggingFace Embedder             │ mmlw-roberta-large (1024 dimensions)
│  (sentence-transformers)          │ Polish legal text specialized
└───────────┬───────────────────────┘
            │
            ▼
┌───────────────────────────────────┐
│  Qdrant Vector Store              │ Index documents by type:
│  (upsert)                         │ • Legal acts collection
│                                   │ • Contracts collection
└───────────────────────────────────┘
```

### Analysis Pipeline (Compliance Check)

```
User initiates: "Run compliance check"
        │
        ▼
┌─────────────────────────────────────┐
│  1. Retrieve Analysis Request       │ From PostgreSQL
│     • Contract document ID          │
│     • Selected legal acts           │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  2. Extract Contract Clauses        │ From Qdrant (contract collection)
│     (LlamaIndex hierarchical search)│
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  3. For each clause:                │
│     a. Query Qdrant (legal acts)    │ RAG context retrieval
│        for relevant regulations     │
│     b. Build prompt with:           │
│        • Clause text                │
│        • Retrieved legal context    │
│        • System instructions        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  4. LLM Analysis (Ollama/Bielik)    │ Compliance check
│     • Detect violations             │ Returns JSON:
│     • Assign severity               │ {findings: [...], score: 0-1}
│     • Generate recommendations      │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  5. Aggregate Report                │ Combine findings
│     • Summary statistics            │ Group by severity
│     • Findings list                 │ Calculate metrics
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  6. Store Report                    │ PostgreSQL
│     • Full report JSON              │ Execution metadata
│     • MLflow experiment tracking    │ Prompt version, model
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  7. Optional: Blockchain Register   │ Hyperledger Fabric
│     • Calculate SHA-256 hash        │ Immutable audit trail
│     • Submit to chaincode           │
└─────────────────────────────────────┘
```

## Project Structure

```
AI-TAURON/
├── src/python/
│   ├── domain/              # Models, ports (Protocol), services
│   ├── adapters/
│   │   ├── ingestion/       # Docling, pdfplumber, chunker
│   │   ├── embedding/       # HuggingFace embedder
│   │   ├── vectorstore/     # Qdrant adapter
│   │   ├── llm/             # Ollama adapter
│   │   ├── rag/             # Compliance prompts, pipeline
│   │   ├── tracking/        # MLflow tracker
│   │   ├── persistence/     # PostgreSQL repository
│   │   └── blockchain/      # Hyperledger Fabric adapter
│   ├── api/                 # FastAPI router, schemas, DI
│   ├── dashboard.py         # Streamlit "Ciocia ALA"
│   ├── config.py            # Pydantic Settings
│   └── main.py              # FastAPI app factory
├── hlf/                     # Hyperledger Fabric
│   ├── fabric-samples/      # Official test-network
│   ├── chaincode-go/        # Compiled chaincode
│   └── gateway-proxy/       # Node.js REST → Fabric SDK
├── scripts/
│   ├── install.sh           # Install / purge / start / stop / status
│   ├── chaincode/           # Go chaincode source
│   ├── download_legal_acts.py
│   ├── generate_contracts.py
│   ├── generate_ground_truth.py
│   └── violation_specs.yaml
├── docker/                  # Dockerfiles (python, mlflow)
├── data/                    # Input data (gitignored)
├── tests/                   # pytest (unit, integration, e2e)
├── docker-compose.yml
├── pyproject.toml
├── CLAUDE.md                # Claude Code project instructions
├── opis-projektu.md         # Full project specification (PL)
├── README.md                # Documentation (PL)
└── README-eng.md            # Documentation (EN) — this file
```

## Test Data (MVP)

The system includes scripts for generating synthetic test data (10 documents):

```bash
# Download legal acts from ISAP (public domain)
python scripts/download_legal_acts.py

# Generate synthetic contracts (requires ANTHROPIC_API_KEY)
python scripts/generate_contracts.py

# Generate ground-truth evaluation dataset
python scripts/generate_ground_truth.py
```

Test data: 2 legal acts + 3 General Terms + 5 contracts with 17 embedded compliance violations.

## Development & Troubleshooting

### Running Tests

```bash
# Unit tests
pytest tests/python -v -m "not integration"

# Integration tests (requires Docker services running)
pytest tests/python -v -m "integration"

# E2E tests (full system)
pytest tests/python -v -m "e2e"

# Coverage report
pytest tests/python --cov=src.python --cov-report=html
```

### Common Issues

**Issue: Ollama connection refused**
```bash
# Verify Ollama is running on host (not in Docker)
curl http://localhost:11434/api/tags
# If needed, check Ollama process
ps aux | grep ollama
```

**Issue: Qdrant connection refused**
```bash
# Verify container is running
docker compose ps qdrant
# Check logs
docker compose logs qdrant
```

**Issue: PostgreSQL authentication failed**
```bash
# Verify credentials in .env match docker-compose.yml
grep POSTGRES_ .env
# Reset database
docker compose down -v  # removes volumes
docker compose up -d postgres
```

**Issue: HLF chaincode deployment fails**
```bash
# Check fabric-samples are downloaded
ls hlf/fabric-samples/
# Verify peer/orderer binaries
ls hlf/bin/
# Restart network
cd hlf && bash setup-fabric.sh restart
```

### Performance Tuning

#### LLM Inference (Ollama)

```bash
# GPU acceleration (if available)
# Edit docker-compose.yml, uncomment deploy.resources.reservations.devices

# CPU cores: Set OLLAMA_NUM_THREAD
docker compose stop ollama
OLLAMA_NUM_THREAD=16 docker compose up -d ollama

# Model quantization
# Default: Q4_K_M (4-bit quantized)
# Options: Q4_0, Q4_K_M, Q5_K_M, Q6_K (larger = slower but better quality)
```

#### Vector Search (Qdrant)

```bash
# Optimize Qdrant memory
# Edit docker-compose.yml environment:
#   QDRANT_STORAGE__SNAPSHOTS_TEMP_DIR: /qdrant/storage/snapshots
#   QDRANT_HTTP__CORS__ALLOWED_ORIGINS: "*"

# Monitor performance
curl http://localhost:6333/metrics
```

#### Embedding Model

```bash
# Default: mmlw-roberta-large (1024 dimensions, slower)
# For faster indexing, use smaller model in config.py:
# EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # 384 dims, fast

# Model download happens on first use, stored in ~/.cache/huggingface
du -sh ~/.cache/huggingface
```

### Debugging

#### Enable verbose logging

Set in `.env`:
```bash
LOG_LEVEL=DEBUG
```

#### View LLM responses

API returns full LLM output in response JSON:
```bash
# Get report with LLM debug info
curl http://localhost:8000/api/v1/reports/{id}?include_debug=true
```

#### Monitor MLflow experiments

```bash
# View all runs
http://localhost:5000

# Query via API
curl http://localhost:5000/api/2.0/mlflow/experiments/list
```

#### Check Qdrant collections

```bash
# List collections
curl http://localhost:6333/collections

# Query specific collection
curl http://localhost:6333/collections/legal-acts/points/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"vector": [...], "limit": 5}'
```

### Docker Compose Profiles

The setup supports Docker profiles for selective service startup:

```bash
# Start only API infrastructure (no UI)
docker compose up -d

# Start with UI
docker compose --profile ui up -d

# Start all (including future observability services)
docker compose --profile ui --profile observability up -d

# List available profiles
grep 'profiles:' docker-compose.yml
```

### Cleanup

```bash
# Stop services (keep data)
docker compose stop

# Stop and remove containers
docker compose down

# Remove all data (volumes)
docker compose down -v

# Full cleanup (remove images too)
docker compose down -v --rmi all
```

## Deployment Checklist

For production deployment:

- [ ] Use HTTPS (reverse proxy with TLS)
- [ ] Set strong `.env` passwords
- [ ] Enable database backups (PostgreSQL)
- [ ] Configure Ollama to run as systemd service (not in Docker)
- [ ] Use managed Qdrant or persistent volumes
- [ ] Set resource limits in docker-compose.yml
- [ ] Enable log aggregation (ELK, Datadog, etc.)
- [ ] Monitor API response times and errors
- [ ] Backup Hyperledger Fabric MSP files if used
- [ ] Test disaster recovery plan

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Follow code style: `ruff check src/`
3. Run tests: `pytest tests/`
4. Submit PR with description

## License

Internal project — on-premise deployment only.

## Contact

hal.dariusz.nowak@gmail.com
