# AlICjA — Pitch Deck

## "Ciocia ALA" — AI Context Analisator
### Automatyczna analiza zgodności umów z przepisami prawa

*Prezentacja dla Przedstawicieli Grupy TAURON*

*ETHSilesia Hackathon 2026* 
---

## 1. JAK JEST DZIŚ

### Problem: ręczna rewizja umów nie nadąża za skalą i tempem zmian

**Skala operacji TAURON:**
- **5,8 mln** umów z klientami (5,4 mln B2C + 0,4 mln B2B)
- **Setki** wzorców OWU i umów szczegółowych
- **Dziesiątki** aktów prawnych wpływających na treść umów
- **Kilkanaście** nowelizacji przepisów rocznie

**Klasyczny proces compliance:**

```
Nowelizacja przepisów → Prawnik czyta ustawę → Ręczna analiza OWU
→ Identyfikacja klauzul do zmiany → Korekta wzorców → Wdrożenie
```

| Problem | Skutek |
|---------|--------|
| Rewizja jednego OWU zajmuje **8-16 godzin** pracy prawnika | Opóźnienia w reakcji na zmiany prawne |
| Prawnik sprawdza selektywnie — **nie każda klauzula** vs **każdy przepis** | Niezgodności umykają uwadze |
| Brak centralnego rejestru analiz | Nie wiadomo co, kiedy i z jakim wynikiem sprawdzono |
| Nowelizacja = **ręczne** przeglądanie portfolio | Miesiące zamiast dni |
| Brak audytowalności procesu | Ryzyko przy kontroli URE/UOKiK |

### Realne ryzyka dla TAURON

| Ryzyko | Przykład | Potencjalny koszt |
|--------|----------|-------------------|
| **Kara URE** | Niezgodność OWU z Prawem energetycznym | Do **15% przychodu** z działalności objętej koncesją |
| **Kara UOKiK** | Klauzule abuzywne w umowach konsumenckich | Do **10% obrotu** (precedens: Energia dla Pokoleń — 7 mln zł, 2024) |
| **Pozwy zbiorowe** | Masowe roszczenia klientów z tytułu wadliwych klauzul | Tysiące roszczeń × kwota per klient |
| **Utrata reputacji** | Negatywny PR → spadek NPS | Cel strategiczny NPS ≥75% w 2035 zagrożony |
| **Opóźnienia wdrożeń** | Nowy produkt (taryfy dynamiczne, PPA) czeka na compliance | Utracone przychody z opóźnionej oferty |

> **Pytanie:** Czy TAURON wie dziś, ile z 5,8 mln obowiązujących umów
> jest w pełni zgodnych z aktualnym stanem prawnym?

---

## 2. CO MOŻNA POPRAWIĆ

### AlICjA — "Ciocia ALA" automatyzuje to, co dziś robią prawnicy miesiącami

```
Nowelizacja przepisów → AlICjA automatycznie sprawdza WSZYSTKIE umowy
→ Raport niezgodności w MINUTACH → Rekomendacje zmian → Blockchain audit trail
```

| Dziś (ręcznie) | Z AlICjA |
|-----------------|----------|
| 8-16h na jedno OWU | **5-10 min** na jedno OWU |
| Selektywna analiza (ludzki błąd) | **Każda klauzula** vs **każdy przepis** |
| Brak rejestru | **Blockchain** — niezmienny dowód analizy |
| Reakcja na nowelizację: **tygodnie** | Reakcja: **godziny** |
| Nowy produkt czeka na compliance | Compliance **w cyklu deweloperskim** |
| Wynik zależy od prawnika | **Powtarzalny**, wersjonowany (MLflow) |

### Co AlICjA robi

1. **Czyta dokument** — parser AI (Docling) rozumie strukturę prawną
   (artykuły, paragrafy, ustępy, klauzule)
2. **Porównuje z bazą prawną** — RAG pipeline wyszukuje powiązane przepisy
   (Prawo energetyczne, ustawa konsumencka, decyzje URE)
3. **Analizuje zgodność** — polski model LLM ocenia każdą klauzulę
4. **Generuje raport** — lista niezgodności z severity, referencjami i rekomendacjami
5. **Rejestruje w blockchain** — hash raportu w prywatnym blockchainie TAURON
   (proof of compliance execution)

### Czego AlICjA NIE robi

- **Nie zastępuje prawnika** — wspiera jego pracę, decyzja jest ludzka
- **Nie wysyła danych na zewnątrz** — 100% on-premise, RODO w pełni
- **Nie jest czarną skrzynką** — każdy wynik jest audytowalny (MLflow + blockchain)

---

## 3. DLACZEGO WARTO — TERAZ

### Zbieżność ze strategią "TAURON NOWA energia" 2025-2035

| Cel strategiczny | Jak AlICjA pomaga |
|-----------------|-------------------|
| **EBITDA >13 mld zł (2035)** | Eliminacja kar regulacyjnych chroni wynik finansowy |
| **40 TWh sprzedaży (2035)** | Wzrost bazy klientów +29% = więcej umów do compliance |
| **Cyfrowa transformacja** | AI compliance = element ekosystemu cyfrowych narzędzi (cel: obsługa 24/7 z AI do 2030) |
| **NPS ≥75% (2035)** | Brak klauzul abuzywnych = mniej reklamacji = wyższy NPS |
| **ESG / Governance** | Blockchain audit trail = Dobre Praktyki GPW, transparentność |
| **Nowe produkty** | Taryfy dynamiczne, PPA, prosumer, EV — każdy nowy produkt wymaga nowych umów |
| **100% smart meters (2030)** | Nowe umowy dystrybucyjne dla 5,9 mln punktów |
| **Neutralność klimatyczna 2040** | Compliance nowych regulacji dot. OZE, dekarbonizacji |
| **Dywidenda od 2028** | Stabilność regulacyjna → stabilność przychodów → zdolność dywidendowa |

### Okno czasowe

- **2025-2026:** Wdrażanie nowych taryf, liberalizacja rynku energii
- **2026-2027:** Wejście nowych regulacji UE (dyrektywy rynkowe)
- **2028-2030:** 100% inteligentnych liczników → miliony nowych umów

> **Im później TAURON wdroży automatyzację compliance,
> tym większe ryzyko przy rosnącej skali operacji.**

---

## 4. REALNA KORZYŚĆ DLA TAURON

### A. Oszczędności bezpośrednie

| Kategoria | Kalkulacja | Oszczędność roczna |
|-----------|-----------|-------------------|
| **Czas pracy prawników** | 200 OWU × 12 h × 400 zł/h = 960 000 zł (ręcznie) → AlICjA: ~15 min na OWU | **~900 000 zł** |
| **Czas reakcji na nowelizację** | 4 tygodnie → 1 dzień (batch analysis) | Wartość szybszego TTM nowych produktów |
| **Outsourcing kancelarii** | Redukcja zleceń zewnętrznych compliance o 60-70% | **500 000 - 1 000 000 zł** |

### B. Mitygacja ryzyk regulacyjnych

| Ryzyko | Prawdopodobieństwo (bez AlICjA) | Potencjalny koszt | Mitygacja |
|--------|-------------------------------|-------------------|-----------|
| **Kara URE za niezgodność OWU** | Średnie (kontrole co 2-3 lata) | 5-50 mln zł (do 15% przychodu koncesyjnego) | AlICjA wykrywa niezgodności proaktywnie |
| **Kara UOKiK za klauzule abuzywne** | Średnie (skargi konsumentów) | 10-100 mln zł (do 10% obrotu) | Automatyczna detekcja Art. 385³ KC |
| **Pozew zbiorowy klientów** | Niskie, ale rosnące | 5-20 mln zł (reputacja + odszkodowania) | Compliance wyprzedza reklamacje |
| **Utrata ratingu inwestycyjnego** | Niskie | Wzrost kosztu finansowania | ESG Governance + blockchain audit |

> **Jedna kara URE lub UOKiK kosztuje więcej niż 10 lat AlICjA.**

### C. Wartość strategiczna

| Korzyść | Wpływ na TAURON |
|---------|-----------------|
| **Szybsze time-to-market** nowych produktów | Compliance w cyklu deweloperskim, nie po nim |
| **Compliance-as-a-service** dla BU | Każda Business Unit zleca analizę samodzielnie (self-service) |
| **Audit trail dla akcjonariuszy** | Dowód due diligence compliance → wartość na GPW |
| **Benchmark prawników** | MLflow porównuje: prawnik vs AI — jakość, pokrycie, czas |
| **Skalowalność** | Od 200 OWU do 5,8 mln umów — ten sam system |
| **Compliance nowych regulacji UE** | Szybka adaptacja do dyrektyw rynkowych (2026-2028) |

### D. ROI

| Koszt | Jednorazowy | Roczny |
|-------|-------------|--------|
| Wdrożenie (serwer, integracja) | ~150 000 zł | — |
| Utrzymanie (licencja, aktualizacje) | — | ~200 000 zł |
| Aktualizacja bazy prawnej | — | ~50 000 zł |
| **Razem (rok 1)** | **~400 000 zł** | |
| **Razem (rok 2+)** | | **~250 000 zł** |

| Korzyść | Roczna |
|---------|--------|
| Oszczędność pracy prawników | ~900 000 zł |
| Redukcja outsourcingu | ~750 000 zł |
| Mitygacja kar (wartość oczekiwana) | ~2 000 000 zł |
| **Razem korzyści** | **~3 650 000 zł** |

> **ROI: ~9x w pierwszym roku. Zwrot inwestycji w ~6 tygodni.**

---

## 5. BLOCKCHAIN TAURON — NATURALNE DOPASOWANIE

### TAURON posiada własny prywatny blockchain

AlICjA jest zaprojektowana do integracji z **prywatnym blockchainem TAURON**.

| Funkcja | Jak AlICjA wykorzystuje blockchain |
|---------|----------------------------------|
| **Proof of compliance** | Każdy raport → SHA-256 hash → zapis on-chain (document_id, verdict, timestamp) |
| **Immutability** | Raz zapisany raport nie może być zmieniony — dowód, że analiza się odbyła |
| **Audit trail** | Kontroler URE/UOKiK może zweryfikować: kiedy, co, z jakim wynikiem |
| **Wersjonowanie** | Nowa analiza tego samego dokumentu → nowy hash → historia zmian |
| **Cross-BU trust** | BU Sprzedaż i BU Obsługa Klienta korzystają z tego samego rejestru |

### Architektura integracji

```
[BU Sprzedaż]     [BU Obsługa]     [BU Nowe Usługi]
      │                 │                  │
      └────────┬────────┘──────────────────┘
               │
        ┌──────▼───────┐
        │    AlICjA    │
        │ (Ciocia ALA) │
        └──────┬───────┘
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
  ┌──────┐ ┌──────┐ ┌──────────────────┐
  │Qdrant│ │  PG  │ │ Blockchain TAURON│
  │(RAG) │ │(dane)│ │  (prywatny)      │
  └──────┘ └──────┘ │                  │
                    │  hash + metadata │
                    │  per raport      │
                    └──────────────────┘
```

### Wartość blockchain w kontekście strategii

- **Dobre Praktyki GPW** — wymóg transparentności procesów (cel strategii ESG)
- **Rating inwestycyjny** — dowód dojrzałości compliance dla agencji ratingowych
- **Dywidenda od 2028** — stabilność regulacyjna buduje zaufanie akcjonariuszy
- **Kontrola regulatora** — preemptive compliance: "sprawdziliśmy, oto dowód"

---

## 6. JAK TO WYGLĄDA W PRAKTYCE

### Scenariusz: Nowelizacja Prawa energetycznego

**Dzień 0:** Wchodzi w życie nowelizacja Art. 5 PE (zmiana wymagań umów)

**Bez AlICjA (dziś):**
1. Prawnik czyta nowelizację (1-2 dni)
2. Identyfikuje potencjalnie dotknięte wzorce (3-5 dni)
3. Ręcznie przegląda każdy OWU (2-4 tygodnie)
4. Przygotowuje rekomendacje zmian (1 tydzień)
5. **Łącznie: 4-6 tygodni** — w tym czasie klienci mają niezgodne umowy

**Z AlICjA:**
1. Administrator wgrywa nowelizację do bazy prawnej (5 min)
2. Uruchamia batch analysis na wszystkich OWU (automatyczne)
3. AlICjA analizuje każdy OWU vs nowy przepis (**1-2 godziny**)
4. Raport z listą niezgodności, severity i rekomendacjami
5. Prawnik weryfikuje i zatwierdza rekomendacje (1 dzień)
6. **Łącznie: 1-2 dni** — 20x szybciej

### Scenariusz: Nowy produkt — taryfa dynamiczna

**Dzień 0:** BU Nowe Usługi przygotowuje umowę na taryfę dynamiczną

1. Prawnik redaguje wzorzec umowy
2. Wgrywa do AlICjA → analiza compliance (**10 min**)
3. AlICjA wykrywa: brak informacji o ryzyku cenowym (wymóg dyrektywy UE)
4. Prawnik koryguje klauzulę przed wdrożeniem
5. **Compliance w cyklu deweloperskim**, nie po nim

### Scenariusz: Kontrola URE

**Dzień 0:** URE żąda dowodów compliance OWU za ostatnie 2 lata

**Bez AlICjA:** "Przepraszamy, nie mamy systematycznej dokumentacji"

**Z AlICjA:**
1. Dashboard → lista wszystkich raportów za 2 lata
2. Blockchain → niezmienny dowód: data, wynik, hash każdej analizy
3. MLflow → parametry: jaki model, jaki prompt, jakie wyniki
4. **"Oto nasze raporty compliance. Każdy zarejestrowany w blockchainie."**

---

## 7. NASTĘPNE KROKI

### Pilotaż (0-6 tygodnia)

| Krok | Opis | Wynik |
|------|------|-------|
| **1. PoC na 10 OWU** | Analiza wybranych wzorców umów ze znanymi niezgodnościami | Walidacja jakości detekcji (precision/recall) |
| **2. Benchmark z prawnikami** | Porównanie: AlICjA vs prawnik na tych samych dokumentach | Dowód skuteczności |
| **3. Integracja z blockchain TAURON** | Podłączenie do prywatnego blockchaina | Proof of concept audit trail |
| **4. Decyzja Go/No-Go** | Na podstawie wyników pilotażu | Przejście do wdrożenia |

### Wdrożenie (6-9 tygodnia)

| Krok | Opis |
|------|------|
| **5. Produkcja** | Deployment on-premise w infrastrukturze TAURON |
| **6. Integracja z DMS** | Połączenie z systemami zarządzania dokumentami |
| **7. Szkolenia** | Warsztaty dla specjalistów compliance i prawników |
| **8. Batch analysis** | Przegląd pełnego portfolio OWU |

### Rozwój (9-15 tygodnia)

| Krok | Opis |
|------|------|
| **9. Nowe typy umów** | Taryfy dynamiczne, PPA, prosumer, EV, B2B |
| **10. Alerty legislacyjne** | Automatyczne monitorowanie zmian prawnych |
| **11. Integracja z Mój TAURON** | Self-service compliance dla BU |
| **12. Fine-tuning modelu** | Dostrojenie na danych TAURON → wyższa jakość |

---

## 8. PODSUMOWANIE

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   AlICjA = oszczędność + bezpieczeństwo + szybkość + audyt      │
│                                                                 │
│   ✅ 20x szybsza analiza compliance (dni → minuty)              │
│   ✅ ROI 9x w pierwszym roku (~3,6 mln zł korzyści)             │
│   ✅ Mitygacja ryzyk regulacyjnych (kary do 10% obrotu)         │
│   ✅ Blockchain TAURON = niezmienny audit trail                 │
│   ✅ 100% on-premise (RODO, cyberbezpieczeństwo)                │
│   ✅ Wprost ze strategii: cyfryzacja + AI + ESG + klient        │
│                                                                 │
│   Koszt: ~400K zł (rok 1) → ~250K zł (rok 2+)                   │
│   Korzyść: ~3,6 mln zł/rok + mitygacja kar >10 mln zł           │
│                                                                 │
│   "Jedna kara URE kosztuje więcej niż 10 lat AlICjA"            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Autorzy

| Rola | Osoba | Odpowiedzialność |
|------|-------|-----------------|
| **Architekt & Business Development** | Dariusz Nowak | Architektura systemu, strategia biznesowa, analiza compliance, integracja ze strategią TAURON |
| **DevOps** | Błażej Krząkała | Infrastruktura, deployment, Docker, Hyperledger Fabric, CI/CD |
| **AI Assistant** | Klaudyna (Claude) | Wsparcie AI — kodowanie, RAG pipeline, generacja dokumentacji, analiza strategii |

---

*AlICjA "Ciocia ALA" — AI Context Analisator*
*Kwiecień 2026*
