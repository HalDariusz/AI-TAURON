# 👩‍⚖️ AlICjA — AI Context Analisator

**"Aunt ALA"** — AI compliance assistant for automated analysis of customer contracts
against energy law regulations, consumer protection acts, and URE (Energy Regulatory Office) requirements.

## Project Overview

AlICjA analyzes documents (energy sale contracts, General Terms & Conditions, comprehensive contracts)
by comparing their clauses against applicable law. The system detects non-compliance issues,
assesses their severity, and generates remediation recommendations — before they become
regulatory risks or grounds for customer complaints.

### Key Features

- **RAG pipeline** — LlamaIndex with hierarchical retrieval (article → paragraph → section)
- **Polish LLM** — Bielik 11B v3.0 (SpeakLeash), natively trained on Polish legal texts
- **Blockchain audit trail** — Hyperledger Fabric, every report registered on-chain (SHA-256)
- **On-premise** — no data leaves the infrastructure (GDPR requirement)
- **MLflow** — experiment tracking, prompt versioning, quality evaluation
- **Structure-aware chunking** — respects legal document hierarchy

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Bielik 11B v3.0 Q4_K_M via Ollama (CPU inference) |
| **RAG** | LlamaIndex + mmlw-roberta-large (1024-dim embeddings) |
| **Vector DB** | Qdrant |
| **Database** | PostgreSQL 17 |
| **Blockchain** | Hyperledger Fabric 2.5 (Go chaincode) |
| **API** | FastAPI + uvicorn |
| **Frontend** | Streamlit ("Aunt ALA") |
| **MLOps** | MLflow |
| **Document parsing** | Docling (IBM) + pdfplumber |
| **Infrastructure** | Docker Compose |

## Requirements

### Server

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 8 cores | 12+ cores |
| **RAM** | 32 GB | 64+ GB (125 GB on hal) |
| **Disk** | 50 GB | 200+ GB |
| **GPU** | not required | optional (speeds up LLM ~10x) |
| **OS** | Ubuntu 22.04+ | Ubuntu 24.04 |

### Software

- Docker 24+ with Docker Compose v2
- Python 3.11+ (conda or venv)
- Node.js 18+ (for HLF gateway proxy)
- Go 1.21+ (chaincode compilation)
- Ollama with Bielik model installed

## Installation

### Quick Start (fresh install)

```bash
git clone https://github.com/HalDariusz/AI-TAURON.git
cd AI-TAURON
./scripts/install.sh install    # infra + HLF + Python deps
./scripts/install.sh start      # launch API + dashboard
```

### install.sh Commands

| Command | Description |
|---------|-------------|
| `install` | Full installation: Docker infra + HLF network + chaincode + Python deps |
| `start` | Start application services (API + Streamlit + HLF proxy) |
| `stop` | Stop application services (Docker infra keeps running) |
| `status` | Show status of all services |
| `purge` | Stop EVERYTHING, remove all data and Docker volumes |
| `reinstall` | Purge + install (clean slate) |

### Step-by-Step Manual Installation

```bash
# 1. Copy configuration
cp .env.example .env
# Edit .env — set passwords, LLM model, parameters

# 2. Start Docker infrastructure
docker compose up -d qdrant postgres
docker compose up -d --build mlflow

# 3. Check Ollama (should be running natively)
curl http://localhost:11434/api/tags
# If Bielik missing: ollama pull SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M

# 4. Install Python
conda create -n ai-tauron python=3.12 -y
conda activate ai-tauron
pip install -e ".[dev,ui]"

# 5. Hyperledger Fabric
cd hlf/fabric-samples/test-network
export PATH="$(pwd)/../bin:$PATH"
./network.sh up createChannel -c compliancech -ca
./network.sh deployCC -ccn compliance-registry \
    -ccp ~/prg/AI-TAURON/hlf/chaincode-go -ccl go -c compliancech

# 6. HLF Gateway proxy
cd ~/prg/AI-TAURON/hlf/gateway-proxy
npm install
CHANNEL=compliancech node server.js &

# 7. Start API
cd ~/prg/AI-TAURON
uvicorn src.python.main:app --host 0.0.0.0 --port 8000

# 8. Start dashboard (separate terminal)
streamlit run src/python/dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## Services

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| 👩‍⚖️ Aunt ALA | 8501 | http://server:8501 | User frontend |
| 🔌 FastAPI | 8000 | http://server:8000 | REST API |
| 📊 MLflow | 5000 | http://server:5000 | Experiment tracking |
| 📦 Qdrant | 6333 | http://server:6333 | Vector DB |
| 🤖 Ollama | 11434 | http://server:11434 | LLM inference |
| 🔗 HLF Proxy | 3001 | http://server:3001 | Blockchain gateway |

## Usage — Happy Path

### 1. Open Aunt ALA

Navigate to `http://server:8501` — you'll see the welcome page with a system summary.

### 2. Add Legal Acts (knowledge base)

First, populate the system with the legal knowledge base — these are the documents contracts will be checked against.

1. Menu → **📤 Add document**
2. Select type: **📜 Legal act**
3. Upload PDF (e.g., Energy Law from ISAP)
4. Click **Upload and index**
5. The system parses the document, splits it into articles, and indexes it in Qdrant
6. Repeat for each legal act

### 3. Add a Contract for Analysis

1. Menu → **📤 Add document**
2. Select type: **📄 Contract** or **📋 General Terms**
3. Upload file (PDF/DOCX/TXT)
4. The system indexes the document → note the **Document ID**

### 4. Run Compliance Analysis

1. Menu → **🔍 Analysis**
2. Select a document from the list (or enter ID manually)
3. On the right side you'll see a **preview** of the document (clauses/articles)
4. Click **Run analysis**
5. Aunt ALA analyzes each clause against the legal knowledge base
6. Result: number of non-compliance findings + severity (critical/high/medium/low)
7. The report is automatically registered on the blockchain

### 5. Browse Reports

1. Menu → **📊 Reports**
2. List of reports with color-coded severity indicators
3. Click on a report → details:
   - Summary
   - List of non-compliance findings with description, violated regulation, and recommendation
   - Model and prompt version used for the analysis

### 6. Verify on Blockchain

1. Menu → **🔗 Blockchain**
2. Select a report from the list or enter ID manually
3. Click **Verify on blockchain**
4. The system compares the current report hash with the on-chain record
5. ✅ Verified = the report has not been modified since the analysis

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check of all services |
| GET | `/api/v1/documents` | List documents in the system |
| GET | `/api/v1/documents/{id}/preview` | Preview document chunks |
| POST | `/api/v1/documents/upload` | Upload and index a document |
| POST | `/api/v1/analysis/run` | Run compliance analysis |
| GET | `/api/v1/reports` | List reports |
| GET | `/api/v1/reports/{id}` | Full report details |
| DELETE | `/api/v1/documents/{id}` | Delete a document |
| POST | `/api/v1/blockchain/verify` | Verify report on blockchain |

API documentation (Swagger): `http://server:8000/docs`

## Architecture

```
                           ┌─────────────────────────────┐
                           │  👩‍⚖️ Aunt ALA (Streamlit)    │
                           │         :8501               │
                           └──────────┬──────────────────┘
                                      │ HTTP
                           ┌──────────▼──────────────────┐
                           │   FastAPI REST API          │
                           │         :8000               │
                           └──┬────┬────┬────┬───────────┘
                              │    │    │    │
                 ┌────────────┘    │    │    └────────────┐
                 ▼                 ▼    ▼                 ▼
          ┌──────────┐    ┌──────────┐ ┌──────────┐ ┌──────────┐
          │  Qdrant  │    │ Ollama   │ │PostgreSQL│ │  MLflow  │
          │  :6333   │    │ :11434   │ │  :5432   │ │  :5000   │
          │Vector DB │    │Bielik 11B│ │ metadata │ │ tracking │
          └──────────┘    └──────────┘ │ reports  │ └──────────┘
                                       └──────────┘
                                            │
                           ┌────────────────▼────────────┐
                           │   Hyperledger Fabric        │
                           │   HLF Proxy :3001           │
                           │   Peer :7051 / :9051        │
                           │   Orderer :7050             │
                           │   Chaincode: compliance-    │
                           │              registry       │
                           └─────────────────────────────┘
```

### Analysis Pipeline

```
[Upload PDF/DOCX] → Docling parser → Structure-aware chunker
                                           ↓
                                    Embedding (mmlw-roberta-large)
                                           ↓
                                    Qdrant (upsert)
                                           ↓
[Analysis] → Retrieve legal context → Build prompt → Bielik 11B → Parse JSON
                                                                      ↓
                                                              ComplianceReport
                                                              ↓           ↓
                                                        PostgreSQL   Hyperledger
                                                        (full report)  (hash)
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
│   ├── dashboard.py         # Streamlit "Aunt ALA"
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

## License

Internal project — on-premise deployment only.

## Contact

AI-TAURON R&D Team
