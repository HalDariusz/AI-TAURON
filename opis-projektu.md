# AlICjA — AI Context Analisator

**Nazwa projektu:** AlICjA (AI Context Analisator)

**Nazwa dla użytkownika:** Ciocia ALA

**Kontekst biznesowy:** AI Asystent compliance — „Ciocia ALA" pomaga specjalistom
i prawnikom w automatycznej weryfikacji zgodności dokumentów z przepisami prawa.

**Przestrzeń:** Obsługa klienta

Automatyczny przegląd umów z klientami pod kątem zgodności z aktualnymi przepisami
prawa energetycznego, ochrony konsumentów i regulacjami URE.

## Cel

**Compliance** — wykrywanie niezgodności w umowach klienckich, zanim staną się
ryzykiem regulacyjnym lub podstawą reklamacji.

Kluczowe pytania, na które system odpowiada:
- Czy klauzule umowy są zgodne z aktualnym stanem prawnym?
- Które zapisy OWU wymagają aktualizacji po zmianach legislacyjnych?
- Jakie ryzyka compliance niosą istniejące umowy?
- Które grupy umów wymagają priorytetowej rewizji?

## Zakres

### Dokumenty wejściowe
- **Umowy szczegółowe** — indywidualne umowy z klientami (sprzedaż, dystrybucja, kompleksowe)
- **OWU** — Ogólne Warunki Świadczenia Usług (wzorce umowne)
- **Akty prawne** — Prawo energetyczne, ustawy, rozporządzenia, decyzje URE, dyrektywy UE

### Produkty wyjściowe
- Raport zgodności per umowa/OWU (lista niezgodności + referencje do przepisów)
- Dashboard zagregowany — mapa ryzyk compliance w portfolio umów
- Alerty przy zmianach legislacyjnych wpływających na istniejące umowy
- Rekomendacje zmian klauzul z uzasadnieniem prawnym

## Architektura

### Wzorzec: Hexagonal Architecture
Separacja logiki domenowej od infrastruktury (LLM, storage, API).
Porty i adaptery umożliwiają wymianę providera LLM lub źródła danych
bez modyfikacji rdzenia.

### Model wiedzy: DIKW
| Warstwa       | Rola w systemie                                              |
|---------------|--------------------------------------------------------------|
| **Data**      | Surowe teksty umów, OWU, aktów prawnych (PDF, DOCX, HTML)   |
| **Information** | Wyekstrahowane klauzule, artykuły, definicje, powiązania  |
| **Knowledge** | Graf zależności: klauzula ↔ przepis, reguły compliance       |
| **Wisdom**    | Ocena ryzyka, priorytetyzacja, rekomendacje działań          |

### Pipeline AI
```
[Dokumenty] → Docling/pdfplumber → Structure-aware → Embedding → Qdrant
                  (parsing)        chunking       (HuggingFace)     ↓
                                  (LlamaIndex)                      ↓
[Query] → LlamaIndex RAG → Hierarchical → Ollama/vLLM → Report → [Output]
          (query engine)    Retrieval          ↑
                ↑                        [MLflow: tracking,
          [Qdrant retrieval]              prompt versioning]
                                               ↑
                                         [Langfuse: tracing,
                                          observability]
```

- **LlamaIndex** — orkiestracja RAG pipeline: hierarchical retriever → query routing
  → prompt template → LLM → structured output
- **MLflow** — śledzenie eksperymentów, wersjonowanie promptów i modeli, ewaluacja jakości
- **Langfuse** — tracing runtime: latency, tokeny, debugowanie per-query
- **RAG** (Retrieval-Augmented Generation) — kontekstowe odpytywanie bazy umów
  i przepisów, minimalizacja halucynacji przez grounding w źródłach
- **LLM** (via Ollama) — analiza semantyczna klauzul, porównanie z wymogami prawnymi,
  generowanie raportów w języku naturalnym

## Technologie

### Języki
- **Python** — cały pipeline: RAG, LLM, document processing, API, ewaluacja
- **Rust** — opcjonalnie w fazie 3, tylko jeśli profiling wykaże bottleneck
  (bottleneck tego systemu to LLM inference, nie I/O)

### RAG Framework
- **LlamaIndex** — primary framework do RAG pipeline
  - Natywny hierarchiczny retrieval (document → section → chunk) — kluczowe
    dla struktury dokumentów prawnych (artykuł → paragraf → ustęp)
  - Query routing — automatyczny dobór strategii wyszukiwania per typ pytania
  - `llama-index-vector-stores-qdrant` — integracja z Qdrant
  - `llama-index-llms-ollama` — integracja z Ollama (on-prem LLM)
  - `llama-index-embeddings-huggingface` — lokalne modele embedding

### MLOps
- **MLflow** — centralna platforma ML lifecycle management
  - **Tracking** — logowanie eksperymentów: parametry modeli, metryki (precision/recall),
    wersje promptów, konfiguracje RAG pipeline
  - **Model Registry** — wersjonowanie modeli LLM i embedding, staging → production
  - **Evaluate** — `mlflow.evaluate()` do oceny jakości odpowiedzi LLM
    (faithfulness, relevance, toxicity)
  - **Prompt Engineering** — wersjonowanie prompt templates w MLflow Tracking
  - **Deployment** — serwowanie modeli via MLflow Serving (REST API, faza 3)
  - Deployment: self-hosted (Docker), backend store: PostgreSQL,
    artifact store: lokalny filesystem (MVP) → MinIO (faza 2+)

### LLM Observability
- **Langfuse** — open-source (MIT), self-hosted tracing i debugowanie pipeline RAG
  - Tracing end-to-end: retrieval → prompt → LLM → output
  - Prompt management i wersjonowanie
  - Metryki per-query: latency, token usage, koszt
  - Integracja z LlamaIndex via callback handler
  - Zastępuje LangSmith (który wymaga licencji enterprise do self-hosted)

### Document Processing
- **Docling (IBM)** — primary parser, Apache 2.0
  - Natywne rozpoznawanie hierarchii sekcji (kluczowe dla aktów prawnych)
  - PDF, DOCX, HTML, obrazy
  - Ekstrakcja tabel, list, nagłówków z zachowaniem struktury
  - OCR via EasyOCR / Tesseract backend
- **pdfplumber** — fallback do niskopoziomowego parsingu PDF (layout-aware)
- **Tesseract OCR** — rozpoznawanie tekstu ze skanowanych dokumentów

### Inference LLM (on-premise)
- **Ollama** — faza 1–2: prosty deployment modeli LLM lokalnie
- **vLLM** — faza 3: wysokowydajny inference server (PagedAttention, continuous batching)

### API / Interfejs
- **FastAPI** — REST API do zlecania analiz i pobierania raportów
  - Endpointy: upload dokumentów, zlecanie analizy, status, pobranie raportu
  - OpenAPI/Swagger — dokumentacja automatyczna
  - Auth: JWT + RBAC (faza 3)
- **Streamlit** — MVP dashboard (faza 1–2), szybkie prototypowanie UI
  - Mapa ryzyk, raporty compliance, podgląd flagowanych klauzul
- **React + Tailwind** — docelowy dashboard produkcyjny (faza 3, opcjonalnie)

### Infrastruktura

### Blockchain (rejestr raportów compliance)
- **Hyperledger Fabric** — prywatny, permissioned blockchain (on-premise)
  - Każdy raport compliance rejestrowany on-chain jako dowód istnienia
  - Zapis: SHA-256 hash raportu + document_id + timestamp + verdict (compliant/non-compliant)
  - Pełny raport off-chain (PostgreSQL) — on-chain tylko fingerprint
  - Tamper-evident: raz zapisany raport nie może być zmieniony ani usunięty
  - Chaincode (smart contract) w Go — walidacja i zapis transakcji
  - Peer node + Orderer node + CA — minimalna topologia MVP
  - Integracja via Hyperledger Fabric SDK for Python (`hfc`)

#### Faza 1 (MVP)
- **Docker Compose** — orkiestracja serwisów
- **Qdrant** — vector DB (embeddingi dokumentów)
- **PostgreSQL** — metadane, audit log, MLflow backend store
- **Hyperledger Fabric** — rejestr raportów (peer, orderer, CA)
- **Lokalny filesystem** — dokumenty oryginalne, MLflow artifacts

#### Faza 2+ (skala)
- **MinIO** — object storage (gdy artifacts MLflow się rozrosną)
- **Langfuse** — observability (self-hosted Docker)

#### Faza 3 (produkcja)
- **vLLM** — zastępuje Ollama
- **nginx / Traefik** — reverse proxy, TLS termination

## Użytkownicy i role

| Rola | Opis | Dostęp |
|------|------|--------|
| **Specjalista compliance** | Główny użytkownik — zleca analizy, przegląda raporty, akceptuje/odrzuca rekomendacje | Pełny dostęp do raportów i dashboardu |
| **Prawnik wewnętrzny** | Weryfikuje rekomendacje systemu, podejmuje decyzje o zmianach klauzul | Raporty + rekomendacje, brak konfiguracji |
| **Menedżer BOK** | Monitoruje zagregowane ryzyka w portfolio umów | Dashboard read-only |
| **Administrator** | Zarządza bazą aktów prawnych, konfiguruje pipeline, zarządza użytkownikami | Pełny dostęp + konfiguracja |

### Flow interakcji (typowy)
1. Administrator wprowadza/aktualizuje bazę aktów prawnych
2. Specjalista compliance zleca analizę partii umów lub OWU
3. System generuje raport zgodności z listą niezgodności
4. Prawnik wewnętrzny weryfikuje flagowane klauzule
5. Specjalista compliance tworzy zlecenia korekty umów

## Fazy / Roadmap

### Faza 1 — MVP (batch analysis)
- Ingestion: Docling + pdfplumber → tekst strukturalny
- LlamaIndex RAG pipeline + Ollama (Bielik 11B, natywnie na hal)
- Baza aktów prawnych: ręczny upload kluczowych ustaw → Qdrant
- MLflow Tracking: logowanie eksperymentów, wersje promptów
- FastAPI: REST API do zlecania analiz
- Streamlit: prosty dashboard do przeglądania raportów
- Raport zgodności per dokument (JSON + Streamlit)
- **Hyperledger Fabric**: rejestr blockchain — hash + metadata każdego raportu
- Scope: wybrane OWU (≤10 dokumentów)
- Infra: Docker Compose (Qdrant + PostgreSQL + MLflow + Hyperledger Fabric)
  + natywny Ollama na hal

### Faza 2 — Skala + alerty
- Streamlit dashboard z mapą ryzyk compliance
- Automatyczne alerty przy zmianach legislacyjnych
- Batch processing pełnego portfolio umów
- Integracja ze źródłem aktów prawnych (ISAP API)
- MLflow Evaluate: systematyczna ewaluacja precision/recall na benchmarku
- MLflow Model Registry: staging → production workflow dla modeli i promptów
- Langfuse: tracing i debugowanie pipeline RAG
- MinIO: object storage dla artifacts
- Benchmark budowany z prawnikami (ground-truth dataset)

### Faza 3 — Produkcja
- Rekomendacje zmian klauzul z uzasadnieniem prawnym
- Audit log + wersjonowanie analiz
- Integracja z systemami wewnętrznymi (DMS, CRM)
- Multi-user z RBAC (JWT + FastAPI)
- React + Tailwind: docelowy dashboard produkcyjny (opcjonalnie)
- vLLM jako inference backend (zastępuje Ollama)
- nginx/Traefik: reverse proxy, TLS
- MLflow Serving: REST API do serwowania modeli
- CI/CD pipeline: automatyczny retrain/redeploy via MLflow + GitHub Actions
- Rust: ewentualna optymalizacja bottlenecków (jeśli profiling wykaże)

## Źródła danych

### Umowy i OWU
- **Format**: PDF (drukowane i skanowane), DOCX, HTML
- **Wolumen**: szacunkowo setki wzorców OWU, tysiące umów szczegółowych
- **Lokalizacja**: do ustalenia (DMS wewnętrzny / share sieciowy / upload)
- **Język**: polski

### Akty prawne i regulacje
- **Prawo energetyczne** (Dz.U. 1997 nr 54 poz. 348 z późn. zm.)
- **Ustawa o ochronie praw konsumentów**
- **Rozporządzenia wykonawcze MKiŚ**
- **Decyzje i komunikaty URE** (taryfy, wzorce umów)
- **Dyrektywy UE** (rynek energii, ochrona konsumentów)
- **Źródło**: ISAP API (isap.sejm.gov.pl) — faza 1: ręczny upload, faza 2: automatyczny pull
- **Aktualizacja**: monitorowanie Dz.U. pod kątem zmian w aktach z zakresu

### Storage
- **Relacyjna DB** (PostgreSQL) — metadane dokumentów, użytkownicy, audit log, wyniki analiz
- **Vector DB** (Qdrant) — embeddingi chunków dokumentów
- **Object storage** — oryginalne pliki dokumentów (lokalne / MinIO)

## Model LLM

### Deployment: on-premise (wymóg)
Dane umów klienckich są danymi wrażliwymi (dane osobowe, warunki handlowe).
Niedopuszczalne jest przesyłanie ich do zewnętrznych API.

### Kandydaci
| Model | Zalety | Wady |
|-------|--------|------|
| **Mistral Large** | Dobra jakość w językach europejskich, dostępny on-prem | Wymagania GPU |
| **Llama 3** | Open-source, duża społeczność, fine-tuning | Słabszy w polskim prawie bez fine-tuningu |
| **Bielik (SpeakLeash)** | Natywnie polski, trenowany na polskich tekstach prawnych | Mniejszy model, ograniczona pojemność kontekstu |

### Decyzja (podjęta 2026-04-18)
**Wybrany model: Bielik 11B v3.0 Instruct (Q4_K_M)** — `SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M`
- Natywnie polski, trenowany na polskich tekstach prawnych
- Dostępny na serwerze hal (natywna instalacja Ollama, CPU inference)
- 11.2B parametrów, ~7 GB RAM w Q4_K_M
- Serwer hal: 125 GB RAM, 12 cores, brak GPU — Bielik na CPU działa (~30s/query)

Dodatkowe modele dostępne na hal do benchmarku:
- `qwen2.5:7b` (Q4_K_M) — multilingual baseline
- `deepseek-r1:latest` (8.2B, Q4_K_M) — reasoning model
- `deepseek-r1:671b` (Q4_K_M) — heavy, do testów jakości

### Embedding model
- **Wybrany**: `sdadas/mmlw-roberta-large` — 1024-dim (po auto-detekcji na hal),
  trenowany na polskich tekstach, dobra jakość retrieval
- **Alternatywa**: `multilingual-e5-large` — 1024-dim, wielojęzyczny

## Strategia chunkingu

Dokumenty prawne mają hierarchiczną strukturę, która musi być zachowana.
Naive chunking po tokenach niszczy kontekst.

### Podejście: structure-aware chunking
1. **Parsing strukturalny** — rozpoznanie hierarchii: dział → rozdział → artykuł → paragraf → ustęp → punkt
2. **Chunk = jednostka logiczna** — artykuł/paragraf jako atomowa jednostka (nie fragment tokenu)
3. **Metadata per chunk** — numer artykułu, akt prawny, data obowiązywania, hierarchia nadrzędna
4. **Overlap kontekstowy** — nagłówek sekcji nadrzędnej dołączany do chunka jako prefix
5. **Umowy** — chunking po klauzulach/sekcjach umowy (preambuła, definicje, prawa, obowiązki, kary)

### Rozmiar chunków
- Target: 512–1024 tokenów per chunk (z metadata prefix)
  — dokumenty prawne są gęste semantycznie, zbyt małe chunki tracą kontekst
- Duże artykuły: split na ustępy z zachowaniem referencji do artykułu
- Dokładny rozmiar do ustalenia empirycznie (benchmark retrieval quality vs chunk size)

## Metryki sukcesu

### Jakość analizy
- **Precision** — % flagowanych niezgodności, które są rzeczywistymi niezgodnościami (cel: ≥85%)
- **Recall** — % rzeczywistych niezgodności wykrytych przez system (cel: ≥90%)
- **Grounding rate** — % rekomendacji z poprawną referencją do przepisu źródłowego

### Efektywność operacyjna
- **Czas analizy** — czas przetworzenia jednej umowy/OWU (cel: <5 min)
- **Pokrycie portfolio** — % umów przeanalizowanych w danym cyklu
- **Czas reakcji na zmianę prawną** — od publikacji zmiany do wygenerowania alertu

### Adopcja
- **Acceptance rate** — % rekomendacji zaakceptowanych przez prawników
- **Czas rewizji** — porównanie: czas manualnej rewizji vs. rewizja z systemem

## Ewaluacja RAG

### Budowa ground-truth datasetu
1. Wybrać 20–50 umów/OWU z **znanymi** niezgodnościami (potwierdzonymi przez prawników)
2. Dla każdej niezgodności: klauzula źródłowa, przepis naruszony, opis niezgodności
3. Format: JSONL — `{document_id, clause, regulation, finding, severity}`
4. Tagowanie: prawnicy wewnętrzni (min. 2 niezależne oceny, inter-annotator agreement)

### Metryki retrieval
- **Hit Rate @k** — czy właściwy chunk pojawia się w top-k wynikach (k=5, 10)
- **MRR (Mean Reciprocal Rank)** — pozycja właściwego chunka w rankingu
- **Context Relevance** — % pobranego kontekstu, który jest istotny dla pytania

### Metryki generacji (via MLflow Evaluate)
- **Faithfulness** — czy odpowiedź jest wierna do pobranego kontekstu (nie halucynuje)
- **Answer Relevance** — czy odpowiedź adresuje pytanie
- **Correctness** — zgodność z ground-truth (porównanie z oceną prawnika)

### Proces benchmarku modeli LLM
1. Przygotować 50+ par (pytanie, oczekiwana odpowiedź) z ground-truth datasetu
2. Uruchomić każdy model kandydata (Mistral, Llama, Bielik) z identycznym promptem
3. Ocenić via MLflow Evaluate: faithfulness, correctness, latency, token usage
4. Wybrać model z najlepszym trade-off: jakość polskiego tekstu prawnego vs. zasoby GPU

## Wymagania sprzętowe

### Serwer hal — stan faktyczny (2026-04-18)
| Komponent | Wartość |
|-----------|---------|
| **OS** | Ubuntu 24.04, kernel 6.8 |
| **CPU** | 12 cores |
| **RAM** | 125 GB |
| **GPU** | brak (CPU-only inference) |
| **Dysk** | 933 GB (160 GB wolne) |
| **Docker** | 28.2.2 + Compose 2.37.1 |
| **Ollama** | natywna instalacja, 8 modeli (w tym Bielik 11B, deepseek-r1 671B) |
| **Python** | 3.12.3 (conda env `ai-tauron`) |

### Deployment model
- **Ollama**: natywnie na hal (nie w Dockerze) — port 11434 na localhost
- **Qdrant + PostgreSQL + MLflow**: Docker Compose
- **FastAPI API**: natywnie w conda env `ai-tauron`
- **Streamlit**: natywnie w conda env `ai-tauron`

### Szacunki RAM per model (CPU inference)
| Model | Quantization | RAM |
|-------|-------------|-----|
| Bielik 11B (wybrany) | Q4_K_M | ~7 GB |
| Bielik 4.5B | FP16 | ~10 GB |
| deepseek-r1 8B | Q4_K_M | ~5 GB |
| deepseek-r1 671B | Q4_K_M | ~400 GB ⚠️ |

### Embedding inference
- `mmlw-roberta-large`: 1024-dim, CPU inference (~3 GB RAM)
- Batch embedding: offline, CPU wystarczy przy 125 GB RAM

## Monitoring produkcyjny (faza 2+)

### Langfuse — runtime observability
- Tracing każdego zapytania: retrieval → prompt → LLM → response
- Latency breakdown per krok pipeline
- Token usage i koszt (nawet on-prem — rozliczanie GPU-hours)
- Feedback loop: prawnik oznacza odpowiedź jako poprawną/błędną → dane do fine-tuningu

### Alerty operacyjne
- LLM inference timeout (>30s per query)
- Qdrant health check (dostępność, rozmiar indeksu)
- Degradacja retrieval quality (spadek hit rate w Langfuse)
- Wolumen przetworzonych dokumentów vs. oczekiwania

### MLflow — offline monitoring
- Drift detection: porównanie metryk nowych eksperymentów vs. baseline
- A/B prompty: porównywanie wariantów prompt templates na tym samym datasecie
- Model decay: periodic re-evaluation na ground-truth datasecie

## Bezpieczeństwo i zgodność

### Klasyfikacja danych
- **Dane osobowe** (RODO) — imiona, nazwiska, adresy, numery klientów w umowach
- **Dane handlowe** — warunki cenowe, rabaty, wolumeny
- **Dane wewnętrzne** — wzorce umów, OWU, strategie compliance

### Wymagania
- **Deployment on-premise** — żadne dane nie opuszczają infrastruktury wewnętrznej
- **Szyfrowanie at-rest** — baza danych, vector store, object storage
- **Szyfrowanie in-transit** — TLS między serwisami
- **RBAC** — dostęp do danych i raportów wg roli użytkownika
- **Audit log** — każda operacja: kto, kiedy, na jakim dokumencie, jaki wynik
- **Retencja** — polityka przechowywania wyników analiz (do ustalenia z compliance)
- **Anonimizacja** — opcjonalna anonimizacja danych osobowych przed analizą LLM

## Ryzyka i ograniczenia

- Jakość analizy zależy od jakości parsingu dokumentów (skanowane PDF → OCR)
- LLM nie zastępuje opinii prawnej — system wspiera, nie decyduje
- Wymaga regularnej aktualizacji bazy aktów prawnych
- Dane umów klienckich = dane wrażliwe → wymóg on-premise / air-gap deployment
- Fine-tuning na domenie prawno-energetycznej może wymagać znacznych zasobów
- Brak ground-truth datasetu — potrzebna walidacja z prawnikami do budowy benchmarku
- Zmiany w strukturze dokumentów (nowe wzorce umów) mogą wymagać rekalibracji parsera
