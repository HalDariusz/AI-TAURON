# 👩‍⚖️ AlICjA — AI Context Analisator

**"Ciocia ALA"** — AI asystent compliance do automatycznej analizy umów z klientami
pod kątem zgodności z przepisami prawa energetycznego, ochrony konsumentów i regulacjami URE.

## Opis projektu

AlICjA analizuje dokumenty (umowy sprzedaży energii, OWU, umowy kompleksowe)
porównując ich klauzule z obowiązującymi przepisami prawa. System wykrywa
niezgodności, ocenia ich wagę i generuje rekomendacje zmian — zanim staną się
ryzykiem regulacyjnym lub podstawą reklamacji klientów.

### Kluczowe cechy

- **RAG pipeline** — LlamaIndex z hierarchicznym retrieval (artykuł → paragraf → ustęp)
- **Polski LLM** — Bielik 11B v3.0 (SpeakLeash), natywnie trenowany na polskich tekstach prawnych
- **Blockchain audit trail** — Hyperledger Fabric, każdy raport rejestrowany on-chain (SHA-256)
- **On-premise** — żadne dane nie opuszczają infrastruktury (wymóg RODO)
- **MLflow** — śledzenie eksperymentów, wersjonowanie promptów, ewaluacja jakości
- **Structure-aware chunking** — respektuje hierarchię dokumentów prawnych

### Stack technologiczny

| Warstwa | Technologia |
|---------|------------|
| **LLM** | Bielik 11B v3.0 Q4_K_M via Ollama (CPU inference) |
| **RAG** | LlamaIndex + mmlw-roberta-large (1024-dim embeddings) |
| **Vector DB** | Qdrant |
| **Baza danych** | PostgreSQL 17 |
| **Blockchain** | Hyperledger Fabric 2.5 (chaincode Go) |
| **API** | FastAPI + uvicorn |
| **Frontend** | Streamlit ("Ciocia ALA") |
| **MLOps** | MLflow |
| **Document parsing** | Docling (IBM) + pdfplumber |
| **Infra** | Docker Compose |

## Wymagania

### Serwer

| Komponent | Minimum | Rekomendowane |
|-----------|---------|---------------|
| **CPU** | 8 cores | 12+ cores |
| **RAM** | 32 GB | 64+ GB (125 GB na hal) |
| **Dysk** | 50 GB | 200+ GB |
| **GPU** | nie wymagane | opcjonalne (przyspiesza LLM ~10x) |
| **OS** | Ubuntu 22.04+ | Ubuntu 24.04 |

### Oprogramowanie

- Docker 24+ z Docker Compose v2
- Python 3.11+ (conda lub venv)
- Node.js 18+ (dla HLF gateway proxy)
- Go 1.21+ (kompilacja chaincode)
- Ollama z zainstalowanym modelem Bielik

## Instalacja

### Szybki start (fresh install)

```bash
git clone <repo-url> AI-TAURON
cd AI-TAURON
./scripts/install.sh install    # infra + HLF + Python deps
./scripts/install.sh start      # uruchom API + dashboard
```

### Komendy install.sh

| Komenda | Opis |
|---------|------|
| `install` | Pełna instalacja: Docker infra + HLF network + chaincode + Python deps |
| `start` | Uruchom serwisy aplikacyjne (API + Streamlit + HLF proxy) |
| `stop` | Zatrzymaj serwisy aplikacyjne (infra Docker nadal działa) |
| `status` | Pokaż status wszystkich serwisów |
| `purge` | Zatrzymaj WSZYSTKO, usuń dane i wolumeny Docker |
| `reinstall` | Purge + install (czysta instalacja od zera) |

### Instalacja krok po kroku (manualna)

```bash
# 1. Skopiuj konfigurację
cp .env.example .env
# Edytuj .env — ustaw hasła, model LLM, parametry

# 2. Uruchom infrastrukturę Docker
docker compose up -d qdrant postgres
docker compose up -d --build mlflow

# 3. Sprawdź Ollama (powinien działać natywnie)
curl http://localhost:11434/api/tags
# Jeśli brak Bielik: ollama pull SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M

# 4. Zainstaluj Python
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

# 7. Uruchom API
cd ~/prg/AI-TAURON
uvicorn src.python.main:app --host 0.0.0.0 --port 8000

# 8. Uruchom dashboard (osobny terminal)
streamlit run src/python/dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## Serwisy

| Serwis | Port | URL | Opis |
|--------|------|-----|------|
| 👩‍⚖️ Ciocia ALA | 8501 | http://server:8501 | Frontend użytkownika |
| 🔌 FastAPI | 8000 | http://server:8000 | REST API |
| 📊 MLflow | 5000 | http://server:5000 | Experiment tracking |
| 📦 Qdrant | 6333 | http://server:6333 | Vector DB |
| 🤖 Ollama | 11434 | http://server:11434 | LLM inference |
| 🔗 HLF Proxy | 3001 | http://server:3001 | Blockchain gateway |

## Użytkowanie — Happy Path

### 1. Otwórz Ciocia ALA

Wejdź na `http://server:8501` — zobaczysz stronę startową z podsumowaniem systemu.

### 2. Dodaj akty prawne (baza wiedzy)

Najpierw zasilaj system bazą prawną — to dokumenty, z którymi porównywane będą umowy.

1. Menu → **📤 Dodaj dokument**
2. Wybierz typ: **📜 Akt prawny**
3. Wgraj PDF (np. Prawo energetyczne z ISAP)
4. Kliknij **Prześlij i zaindeksuj**
5. System parsuje dokument, dzieli na artykuły i indeksuje w Qdrant
6. Powtórz dla każdego aktu prawnego

### 3. Dodaj umowę do analizy

1. Menu → **📤 Dodaj dokument**
2. Wybierz typ: **📄 Umowa** lub **📋 OWU**
3. Wgraj plik (PDF/DOCX/TXT)
4. System zaindeksuje dokument → zanotuj **ID dokumentu**

### 4. Uruchom analizę compliance

1. Menu → **🔍 Analiza**
2. Wybierz dokument z listy (lub wpisz ID)
3. Po prawej stronie zobaczysz **podgląd** dokumentu (klauzule/artykuły)
4. Kliknij **Uruchom analizę**
5. Ciocia ALA przeanalizuje każdą klauzulę vs. baza prawna
6. Wynik: liczba niezgodności + severity (critical/high/medium/low)
7. Raport jest automatycznie rejestrowany w blockchain

### 5. Przeglądaj raporty

1. Menu → **📊 Raporty**
2. Lista raportów z kolorowymi wskaźnikami severity
3. Kliknij na raport → szczegóły:
   - Podsumowanie
   - Lista niezgodności z opisem, naruszonym przepisem i rekomendacją
   - Model i wersja promptu użyte do analizy

### 6. Weryfikuj w blockchain

1. Menu → **🔗 Blockchain**
2. Wybierz raport z listy lub wpisz ID ręcznie
3. Kliknij **Zweryfikuj w blockchain**
4. System porównuje aktualny hash raportu z zapisem on-chain
5. ✅ Zweryfikowany = raport nie był modyfikowany po analizie

## API — endpointy

| Method | Path | Opis |
|--------|------|------|
| GET | `/api/v1/health` | Health check wszystkich serwisów |
| GET | `/api/v1/documents` | Lista dokumentów w systemie |
| GET | `/api/v1/documents/{id}/preview` | Podgląd chunków dokumentu |
| POST | `/api/v1/documents/upload` | Upload i indeksacja dokumentu |
| POST | `/api/v1/analysis/run` | Uruchom analizę compliance |
| GET | `/api/v1/reports` | Lista raportów |
| GET | `/api/v1/reports/{id}` | Pełny raport |
| DELETE | `/api/v1/documents/{id}` | Usuń dokument |
| POST | `/api/v1/blockchain/verify` | Weryfikacja raportu w blockchain |

Dokumentacja API (Swagger): `http://server:8000/docs`

## Architektura

```
                           ┌─────────────────────────────┐
                           │  👩‍⚖️ Ciocia ALA (Streamlit)  │
                           │        :8501                │
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

### Pipeline analizy

```
[Upload PDF/DOCX] → Docling parser → Structure-aware chunker
                                           ↓
                                    Embedding (mmlw-roberta-large)
                                           ↓
                                    Qdrant (upsert)
                                           ↓
[Analiza] → Retrieve legal context → Build prompt → Bielik 11B → Parse JSON
                                                                      ↓
                                                              ComplianceReport
                                                              ↓           ↓
                                                        PostgreSQL   Hyperledger
                                                        (full report)  (hash)
```

## Struktura projektu

```
AI-TAURON/
├── src/python/
│   ├── domain/              # Modele, porty (Protocol), serwisy
│   ├── adapters/
│   │   ├── ingestion/       # Docling, pdfplumber, chunker
│   │   ├── embedding/       # HuggingFace embedder
│   │   ├── vectorstore/     # Qdrant adapter
│   │   ├── llm/             # Ollama adapter
│   │   ├── rag/             # Prompty compliance, pipeline
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
├── data/                    # Dane wejściowe (gitignored)
├── tests/                   # pytest (unit, integration, e2e)
├── docker-compose.yml
├── pyproject.toml
├── CLAUDE.md                # Claude Code project instructions
├── opis-projektu.md         # Pełna specyfikacja projektu (PL)
└── README.md                # Ten plik
```

## Dane testowe MVP

System zawiera skrypty do generacji syntetycznych danych testowych (10 dokumentów):

```bash
# Pobierz akty prawne z ISAP (public domain)
python scripts/download_legal_acts.py

# Wygeneruj syntetyczne umowy (wymaga ANTHROPIC_API_KEY)
python scripts/generate_contracts.py

# Wygeneruj ground-truth dataset
python scripts/generate_ground_truth.py
```

Dane testowe: 2 akty prawne + 3 OWU + 5 umów z 17 osadzonymi naruszeniami compliance.

## Licencja

Projekt wewnętrzny — on-premise deployment.

## Kontakt

AI-TAURON R&D Team
