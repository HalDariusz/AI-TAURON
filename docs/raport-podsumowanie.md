# AlICjA „Ciocia ALA" — Podsumowanie projektu

## Projekt wyróżniony przez Grupę TAURON na ETHSilesia Hackathon 2026

---

## Czym jest AlICjA?

**AlICjA** (AI Context Analisator) to system sztucznej inteligencji do automatycznej weryfikacji zgodności umów z przepisami prawa energetycznego, ochrony konsumentów i regulacjami URE. Przyjazna twarz systemu — interfejs użytkownika — nosi nazwę **„Ciocia ALA"**.

System powstał z myślą o TAURON Polska Energia — największym dystrybutorze energii w Polsce, obsługującym **5,8 mln klientów** (5,4 mln B2C i 0,4 mln B2B). Przy tej skali ręczna weryfikacja zgodności umów to wąskie gardło niemożliwe do przezwyciężenia bez automatyzacji.

---

## Problem, który rozwiązujemy

### Ręczna rewizja nie nadąża za skalą

TAURON zarządza setkami wzorców OWU i tysięcami umów szczegółowych, a obowiązujące przepisy zmieniają się kilkanaście razy w roku. Klasyczny proces compliance wygląda następująco:

```
Nowelizacja przepisów → Prawnik czyta ustawę → Ręczna analiza OWU
→ Identyfikacja klauzul → Korekta wzorców → Wdrożenie
```

Rewizja jednego OWU zajmuje **8–16 godzin** pracy prawnika. Reakcja na jedną nowelizację — **4–6 tygodni**. W tym czasie klienci mają umowy niezgodne z aktualnym stanem prawnym.

### Realne ryzyka finansowe

| Ryzyko regulacyjne | Potencjalny koszt |
|-------------------|------------------|
| Kara URE za niezgodność OWU | do **15% przychodu** z działalności koncesjonowanej |
| Kara UOKiK za klauzule abuzywne | do **10% obrotu** (precedens: Energia dla Pokoleń — 7 mln zł, 2024) |
| Pozwy zbiorowe klientów | miliony złotych + utrata reputacji |
| Opóźnienia wdrożeń nowych produktów | utracone przychody |

> Jedna kara URE lub UOKiK kosztuje więcej niż **10 lat użytkowania AlICjA**.

---

## Jak działa AlICjA

System przechodzi przez pięć kroków dla każdego analizowanego dokumentu:

1. **Czyta dokument** — parser AI (Docling/IBM) rozumie hierarchię prawną: artykuły, paragrafy, ustępy, klauzule.
2. **Porównuje z bazą prawną** — pipeline RAG (LlamaIndex + Qdrant) wyszukuje powiązane przepisy z Prawa energetycznego, ustawy konsumenckiej i decyzji URE.
3. **Analizuje zgodność** — polski model językowy **Bielik 11B** (SpeakLeash), trenowany natywnie na polskich tekstach prawnych, ocenia każdą klauzulę.
4. **Generuje raport** — lista niezgodności z klasyfikacją wagi (critical / high / medium / low), referencjami do konkretnych przepisów i rekomendacjami zmian.
5. **Rejestruje w blockchain** — hash raportu trafia do prywatnego Hyperledger Fabric. Niezmienny dowód, że analiza się odbyła, kiedy i z jakim wynikiem.

---

## Wyniki: czas analizy

| Etap | Bez AlICjA (ręcznie) | Z AlICjA |
|------|---------------------|----------|
| Analiza jednego OWU | 8–16 godzin | **5–10 minut** |
| Reakcja na nowelizację prawa | 4–6 tygodni | **1–2 dni** |
| Pokrycie: klauzule vs przepisy | selektywne (błąd ludzki) | **każda klauzula × każdy przepis** |
| Audytowalność | brak centralnego rejestru | **blockchain — niezmienny dowód** |
| Powtarzalność | zależy od prawnika | **wersjonowany (MLflow)** |

---

## Wpływ biznesowy — kalkulacja ROI

### Oszczędności bezpośrednie (szacunki roczne)

| Kategoria | Oszczędność |
|-----------|-------------|
| Czas pracy prawników (200 OWU × 12h × 400 zł/h → 5 min z AlICjA) | ~900 000 zł |
| Redukcja outsourcingu kancelarii zewnętrznych (–60–70%) | ~750 000 zł |
| Wartość oczekiwana mitygacji kar regulacyjnych | ~2 000 000 zł |
| **Razem korzyści roczne** | **~3 650 000 zł** |

### Koszty wdrożenia

| Koszt | Wartość |
|-------|---------|
| Rok 1 (wdrożenie + integracja + utrzymanie) | ~400 000 zł |
| Rok 2+ (utrzymanie + aktualizacje) | ~250 000 zł/rok |

> **ROI: ~9x w pierwszym roku. Zwrot inwestycji w około 6 tygodni.**

*Kalkulacje oparte na szacunkach branżowych. Dokładne wartości do weryfikacji po audycie procesów compliance TAURON.*

---

## Zgodność ze strategią „TAURON NOWA energia" 2025–2035

Projekt nie jest oderwany od kierunku rozwoju spółki — każda funkcja AlICjA wpisuje się w cele strategiczne opublikowane w grudniu 2024 roku.

| Cel strategiczny TAURON | Jak AlICjA pomaga |
|------------------------|-------------------|
| **EBITDA >13 mld zł (2035)** | Eliminacja kar regulacyjnych chroni wynik finansowy |
| **40 TWh sprzedaży (+29%, 2035)** | Wzrost bazy klientów = więcej umów do compliance — skalowalność systemu |
| **NPS ≥75% (2035)** | Automatyczne wykrywanie klauzul abuzywnych → mniej reklamacji → wyższy NPS |
| **Cyfryzacja i AI (obsługa 24/7 do 2030)** | AlICjA to AI compliance jako element cyfrowego ekosystemu obsługi |
| **100% smart meters (2030)** | Miliony nowych umów dystrybucyjnych i prosumenckich do weryfikacji |
| **ESG / Dobre Praktyki GPW** | Blockchain audit trail = transparentność procesów dla akcjonariuszy i regulatorów |
| **Dywidenda od 2028** | Stabilność regulacyjna buduje zaufanie rynku |
| **Nowe produkty (EV, PPA, taryfy dynamiczne)** | Compliance w cyklu deweloperskim, nie po nim |

---

## Kluczowe cechy techniczne

### Architektura zaprojektowana pod bezpieczeństwo danych

- **100% on-premise** — żadne dane klientów nie opuszczają infrastruktury TAURON (wymóg RODO i cyberbezpieczeństwa)
- **Polski model LLM** — Bielik 11B v3.0 (SpeakLeash), trenowany natywnie na polskich tekstach prawnych
- **Hierarchiczny RAG** — LlamaIndex z retrieval respektującym strukturę dokumentów prawnych (artykuł → paragraf → ustęp)
- **Blockchain audit trail** — Hyperledger Fabric: każdy raport jako SHA-256 hash + timestamp + verdict on-chain, nieedytowalny
- **MLflow** — pełna historia eksperymentów, wersjonowanie promptów, ewaluacja precision/recall
- **Structure-aware chunking** — parsowanie zachowuje hierarchię prawną, nie niszczy kontekstu

### Stack technologiczny (w całości open-source)

| Warstwa | Technologia |
|---------|------------|
| LLM | Bielik 11B v3.0 via Ollama |
| RAG | LlamaIndex + mmlw-roberta-large (embeddings) |
| Vector DB | Qdrant |
| Baza danych | PostgreSQL 17 |
| Blockchain | Hyperledger Fabric 2.5 (chaincode Go) |
| API | FastAPI |
| Interfejs | Streamlit „Ciocia ALA" |
| MLOps | MLflow |
| Document parsing | Docling (IBM) + pdfplumber |

---

## Scenariusz kontroli URE — demonstracja wartości

**Sytuacja:** URE żąda dowodów zgodności OWU za ostatnie 2 lata.

**Bez AlICjA:** *„Przepraszamy, nie mamy systematycznej dokumentacji."*

**Z AlICjA:**
1. Dashboard → pełna lista raportów compliance za żądany okres
2. Blockchain → niezmienny dowód: data, wynik, hash każdej analizy
3. MLflow → parametry: model, prompt, metryki jakości
4. **„Oto nasze raporty compliance. Każdy zarejestrowany w blockchainie."**

---

## Zespół

| Rola | Osoba |
|------|-------|
| Architekt & Business Development | **Dariusz Nowak** |
| DevOps & Infrastructure | **Błażej Krząkała** |

---

## Dane i źródła

Wszystkie liczby dotyczące Grupy TAURON (liczba klientów, cele EBITDA, wolumeny sprzedaży, CAPEX) pochodzą wprost z oficjalnej **Strategii Grupy TAURON na lata 2025–2035 „TAURON NOWA energia"** (grudzień 2024). Dane dotyczące kar regulacyjnych opierają się na Art. 56 Prawa energetycznego (URE), Art. 106 ustawy o ochronie konkurencji i konsumentów (UOKiK) oraz decyzjach publicznych organu.

---

*ETHSilesia Hackathon 2026 · Projekt wyróżniony przez Grupę TAURON*
