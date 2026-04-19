# AlICjA — Pitch Deck

## "Aunt ALA" — AI Context Analisator
### Automated contract compliance analysis against legal regulations

*Presentation for TAURON Group Representatives*

*ETHSilesia Hackathon 2026*
---

## 1. WHERE WE ARE TODAY

### Problem: manual contract review can't keep up with scale and pace of change

**TAURON's operational scale:**
- **5.8 million** customer contracts (5.4M B2C + 0.4M B2B)
- **Hundreds** of General Terms & Conditions (OWU) and contract templates
- **Dozens** of legal acts affecting contract content
- **Over a dozen** legislative amendments per year

**Traditional compliance process:**

```
Legislative change → Lawyer reads the act → Manual OWU review
→ Identification of clauses to amend → Template correction → Implementation
```

| Problem | Consequence |
|---------|------------|
| Reviewing a single OWU takes **8–16 hours** of a lawyer's work | Delays in responding to legal changes |
| Lawyer reviews selectively — **not every clause** vs **every regulation** | Non-compliance issues go unnoticed |
| No central analysis registry | Unknown what, when, and with what result was reviewed |
| Amendment = **manual** portfolio review | Months instead of days |
| No process auditability | Risk during URE/UOKiK inspections |

### Real risks for TAURON

| Risk | Example | Potential cost |
|------|---------|---------------|
| **URE penalty** | OWU non-compliance with Energy Law | Up to **15% of revenue** from licensed activities |
| **UOKiK penalty** | Abusive clauses in consumer contracts | Up to **10% of turnover** (precedent: Energia dla Pokolen — PLN 7M, 2024) |
| **Class action lawsuits** | Mass customer claims for defective clauses | Thousands of claims × amount per customer |
| **Reputation damage** | Negative PR → NPS decline | Strategic target NPS ≥75% by 2035 at risk |
| **Implementation delays** | New product (dynamic tariffs, PPA) waiting for compliance | Lost revenue from delayed offering |

> **Question:** Does TAURON know today how many of its 5.8 million active contracts
> are fully compliant with current legislation?

---

## 2. WHAT CAN BE IMPROVED

### AlICjA — "Aunt ALA" automates what lawyers currently do over months

```
Legislative change → AlICjA automatically checks ALL contracts
→ Non-compliance report in MINUTES → Remediation recommendations → Blockchain audit trail
```

| Today (manual) | With AlICjA |
|----------------|-------------|
| 8–16h per OWU | **5–10 min** per OWU |
| Selective analysis (human error) | **Every clause** vs **every regulation** |
| No registry | **Blockchain** — immutable proof of analysis |
| Response to amendment: **weeks** | Response: **hours** |
| New product waits for compliance | Compliance **in the development cycle** |
| Result depends on the lawyer | **Repeatable**, versioned (MLflow) |

### What AlICjA does

1. **Reads the document** — AI parser (Docling) understands legal structure
   (articles, paragraphs, sections, clauses)
2. **Compares with legal base** — RAG pipeline retrieves relevant regulations
   (Energy Law, Consumer Protection Act, URE decisions)
3. **Analyzes compliance** — Polish LLM evaluates each clause
4. **Generates a report** — list of non-compliance issues with severity, references, and recommendations
5. **Registers on blockchain** — report hash in TAURON's private blockchain
   (proof of compliance execution)

### What AlICjA does NOT do

- **Does not replace the lawyer** — supports their work, the decision is human
- **Does not send data externally** — 100% on-premise, full GDPR compliance
- **Is not a black box** — every result is auditable (MLflow + blockchain)

---

## 3. WHY IT'S WORTH IT — NOW

### Alignment with "TAURON NOWA energia" strategy 2025–2035

| Strategic goal | How AlICjA helps |
|----------------|-----------------|
| **EBITDA >PLN 13B (2035)** | Elimination of regulatory penalties protects financial results |
| **40 TWh sales (2035)** | Customer base growth +29% = more contracts for compliance |
| **Digital transformation** | AI compliance = part of the digital tools ecosystem (goal: 24/7 AI-powered service by 2030) |
| **NPS ≥75% (2035)** | No abusive clauses = fewer complaints = higher NPS |
| **ESG / Governance** | Blockchain audit trail = Warsaw Stock Exchange Best Practices, transparency |
| **New products** | Dynamic tariffs, PPA, prosumer, EV — every new product requires new contracts |
| **100% smart meters (2030)** | New distribution contracts for 5.9 million connection points |
| **Climate neutrality 2040** | Compliance with new RES and decarbonization regulations |
| **Dividend from 2028** | Regulatory stability → revenue stability → dividend capacity |

### Window of opportunity

- **2025–2026:** Implementation of new tariffs, energy market liberalization
- **2026–2027:** New EU regulations coming into force (market directives)
- **2028–2030:** 100% smart meters → millions of new contracts

> **The later TAURON implements compliance automation,
> the greater the risk as operations scale up.**

---

## 4. REAL BENEFIT FOR TAURON

### A. Direct savings

| Category | Calculation | Annual savings |
|----------|-----------|----------------|
| **Lawyer time** | 200 OWU × 12h × PLN 400/h = PLN 960,000 (manual) → AlICjA: ~15 min per OWU | **~PLN 900,000** |
| **Response time to amendments** | 4 weeks → 1 day (batch analysis) | Value of faster TTM for new products |
| **Law firm outsourcing** | 60–70% reduction in external compliance engagements | **PLN 500,000 – 1,000,000** |

### B. Regulatory risk mitigation

| Risk | Probability (without AlICjA) | Potential cost | Mitigation |
|------|-------------------------------|---------------|------------|
| **URE penalty for OWU non-compliance** | Medium (inspections every 2–3 years) | PLN 5–50M (up to 15% of licensed revenue) | AlICjA detects non-compliance proactively |
| **UOKiK penalty for abusive clauses** | Medium (consumer complaints) | PLN 10–100M (up to 10% of turnover) | Automatic detection of Art. 385³ of Civil Code |
| **Class action lawsuit** | Low but rising | PLN 5–20M (reputation + damages) | Compliance precedes complaints |
| **Investment rating downgrade** | Low | Increased cost of financing | ESG Governance + blockchain audit |

> **A single URE or UOKiK penalty costs more than 10 years of AlICjA.**

### C. Strategic value

| Benefit | Impact on TAURON |
|---------|-----------------|
| **Faster time-to-market** for new products | Compliance in the development cycle, not after it |
| **Compliance-as-a-service** for BUs | Each Business Unit commissions analysis independently (self-service) |
| **Audit trail for shareholders** | Proof of compliance due diligence → value on WSE |
| **Lawyer benchmarking** | MLflow compares: lawyer vs AI — quality, coverage, time |
| **Scalability** | From 200 OWU to 5.8 million contracts — same system |
| **New EU regulation compliance** | Rapid adaptation to market directives (2026–2028) |

### D. ROI

| Cost | One-time | Annual |
|------|----------|--------|
| Implementation (server, integration) | ~PLN 150,000 | — |
| Maintenance (license, updates) | — | ~PLN 200,000 |
| Legal database updates | — | ~PLN 50,000 |
| **Total (Year 1)** | **~PLN 400,000** | |
| **Total (Year 2+)** | | **~PLN 250,000** |

| Benefit | Annual |
|---------|--------|
| Lawyer time savings | ~PLN 900,000 |
| Outsourcing reduction | ~PLN 750,000 |
| Penalty mitigation (expected value) | ~PLN 2,000,000 |
| **Total benefits** | **~PLN 3,650,000** |

> **ROI: ~9x in the first year. Payback period: ~6 weeks.**

---

## 5. TAURON BLOCKCHAIN — NATURAL FIT

### TAURON has its own private blockchain

AlICjA is designed to integrate with **TAURON's private blockchain**.

| Function | How AlICjA uses blockchain |
|----------|---------------------------|
| **Proof of compliance** | Each report → SHA-256 hash → on-chain record (document_id, verdict, timestamp) |
| **Immutability** | Once recorded, the report cannot be altered — proof that the analysis took place |
| **Audit trail** | URE/UOKiK inspector can verify: when, what, with what result |
| **Versioning** | New analysis of the same document → new hash → change history |
| **Cross-BU trust** | Sales BU and Customer Service BU use the same registry |

### Integration architecture

```
[Sales BU]        [Customer Service]    [New Services BU]
      │                 │                      │
      └────────┬────────┘──────────────────────┘
               │
        ┌──────▼───────┐
        │    AlICjA    │
        │ (Aunt ALA)   │
        └──────┬───────┘
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
  ┌──────┐ ┌──────┐ ┌──────────────────┐
  │Qdrant│ │  PG  │ │ TAURON Blockchain│
  │(RAG) │ │(data)│ │  (private)       │
  └──────┘ └──────┘ │                  │
                    │  hash + metadata │
                    │  per report      │
                    └──────────────────┘
```

### Blockchain value in strategic context

- **WSE Best Practices** — process transparency requirement (ESG strategy goal)
- **Investment rating** — proof of compliance maturity for rating agencies
- **Dividend from 2028** — regulatory stability builds shareholder confidence
- **Regulatory inspection** — preemptive compliance: "we checked, here's the proof"

---

## 6. HOW IT WORKS IN PRACTICE

### Scenario: Energy Law amendment

**Day 0:** An amendment to Art. 5 of the Energy Law takes effect (contract requirements change)

**Without AlICjA (today):**
1. Lawyer reads the amendment (1–2 days)
2. Identifies potentially affected templates (3–5 days)
3. Manually reviews each OWU (2–4 weeks)
4. Prepares remediation recommendations (1 week)
5. **Total: 4–6 weeks** — during which customers hold non-compliant contracts

**With AlICjA:**
1. Administrator uploads the amendment to the legal database (5 min)
2. Launches batch analysis on all OWU (automated)
3. AlICjA analyzes each OWU vs the new regulation (**1–2 hours**)
4. Report with list of non-compliance issues, severity, and recommendations
5. Lawyer reviews and approves recommendations (1 day)
6. **Total: 1–2 days** — 20x faster

### Scenario: New product — dynamic tariff

**Day 0:** New Services BU prepares a contract for a dynamic tariff

1. Lawyer drafts the contract template
2. Uploads to AlICjA → compliance analysis (**10 min**)
3. AlICjA detects: missing price risk information (EU directive requirement)
4. Lawyer corrects the clause before deployment
5. **Compliance in the development cycle**, not after it

### Scenario: URE inspection

**Day 0:** URE requests OWU compliance evidence for the last 2 years

**Without AlICjA:** "We're sorry, we don't have systematic documentation"

**With AlICjA:**
1. Dashboard → list of all reports for the past 2 years
2. Blockchain → immutable proof: date, result, hash of each analysis
3. MLflow → parameters: which model, which prompt, what results
4. **"Here are our compliance reports. Each one registered on the blockchain."**

---

## 7. NEXT STEPS

### Pilot (weeks 0–6)

| Step | Description | Outcome |
|------|-------------|---------|
| **1. PoC on 10 OWU** | Analysis of selected contract templates with known non-compliance issues | Validation of detection quality (precision/recall) |
| **2. Lawyer benchmark** | Comparison: AlICjA vs lawyer on the same documents | Proof of effectiveness |
| **3. TAURON blockchain integration** | Connection to the private blockchain | Proof of concept audit trail |
| **4. Go/No-Go decision** | Based on pilot results | Proceed to implementation |

### Implementation (weeks 6–9)

| Step | Description |
|------|-------------|
| **5. Production** | On-premise deployment in TAURON infrastructure |
| **6. DMS integration** | Connection with document management systems |
| **7. Training** | Workshops for compliance specialists and lawyers |
| **8. Batch analysis** | Full OWU portfolio review |

### Growth (weeks 9–15)

| Step | Description |
|------|-------------|
| **9. New contract types** | Dynamic tariffs, PPA, prosumer, EV, B2B |
| **10. Legislative alerts** | Automatic monitoring of legal changes |
| **11. Mój TAURON integration** | Self-service compliance for BUs |
| **12. Model fine-tuning** | Tuning on TAURON data → higher quality |

---

## 8. SUMMARY

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   AlICjA = savings + security + speed + audit                    │
│                                                                  │
│   ✅ 20x faster compliance analysis (days → minutes)             │
│   ✅ 9x ROI in the first year (~PLN 3.6M in benefits)            │
│   ✅ Regulatory risk mitigation (penalties up to 10% of turnover)│
│   ✅ TAURON blockchain = immutable audit trail                   │
│   ✅ 100% on-premise (GDPR, cybersecurity)                       │
│   ✅ Directly from strategy: digitization + AI + ESG + customer  │
│                                                                  │
│   Cost: ~PLN 400K (Year 1) → ~PLN 250K (Year 2+)                 │
│   Benefit: ~PLN 3.6M/year + penalty mitigation >PLN 10M          │
│                                                                  │
│   "A single URE penalty costs more than 10 years of AlICjA"      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Authors

| Role | Person | Responsibility |
|------|--------|---------------|
| **Architect & Business Development** | Dariusz Nowak | System architecture, business strategy, compliance analysis, TAURON strategy alignment |
| **DevOps** | Blazej Krzakala | Infrastructure, deployment, Docker, Hyperledger Fabric, CI/CD |
| **AI Assistant** | Klaudyna (Claude) | AI support — coding, RAG pipeline, documentation generation, strategy analysis |

---

*AlICjA "Aunt ALA" — AI Context Analisator*
*April 2026*
