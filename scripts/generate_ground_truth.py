#!/usr/bin/env python3
"""Generate ground-truth JSONL files for AI-TAURON MVP evaluation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

SPECS_FILE = Path(__file__).parent / "violation_specs.yaml"
OUTPUT_DIR = Path(__file__).parent.parent / "tests" / "fixtures" / "ground_truth"


def main():
    print("=== AI-TAURON: Generating ground-truth dataset ===\n")

    with open(SPECS_FILE, encoding="utf-8") as f:
        specs = yaml.safe_load(f)

    violation_types = specs["violation_types"]
    documents = specs["documents"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- violations.jsonl ---
    violations = []
    counter = 1
    for doc in documents:
        for v in doc.get("violations", []):
            vtype = violation_types[v["type"]]
            violations.append({
                "id": f"v-{counter:03d}",
                "document_id": doc["id"],
                "violation_type": v["type"],
                "severity": vtype["severity"],
                "clause_location": v["location"],
                "clause_detail": v["detail"],
                "violated_regulation": vtype["regulation"],
                "violation_description": vtype["description"],
                "expected_finding": f"{v['detail']} — naruszenie {vtype['regulation']}",
            })
            counter += 1

    violations_file = OUTPUT_DIR / "violations.jsonl"
    with open(violations_file, "w", encoding="utf-8") as f:
        for v in violations:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    print(f"  violations.jsonl: {len(violations)} entries")

    # --- test_queries.jsonl ---
    queries = [
        {
            "id": "q-001",
            "query": "Jaki jest maksymalny dopuszczalny okres wypowiedzenia umowy "
            "sprzedaży energii dla konsumenta?",
            "expected_source_documents": ["prawo_energetyczne"],
            "expected_chunks_contain": ["Art. 4j", "okres wypowiedzenia"],
            "query_type": "factual",
        },
        {
            "id": "q-002",
            "query": "Sprawdź zgodność klauzuli wypowiedzenia w OWU sprzedaży v2 "
            "z Prawem energetycznym.",
            "expected_source_documents": ["owu_sprzedaz_v2", "prawo_energetyczne"],
            "expected_violations_found": ["V01"],
            "query_type": "compliance_check",
        },
        {
            "id": "q-003",
            "query": "Czy umowa kompleksowa 01 zawiera klauzule abuzywne?",
            "expected_source_documents": ["umowa_kompleksowa_01"],
            "expected_violations_found": ["V05"],
            "query_type": "compliance_check",
        },
        {
            "id": "q-004",
            "query": "Jakie informacje musi zawierać umowa sprzedaży energii elektrycznej?",
            "expected_source_documents": ["prawo_energetyczne"],
            "expected_chunks_contain": ["Art. 5", "umowa sprzedaży"],
            "query_type": "factual",
        },
        {
            "id": "q-005",
            "query": "Czy konsument ma prawo do odstąpienia od umowy sprzedaży energii?",
            "expected_source_documents": ["prawa_konsumenta"],
            "expected_chunks_contain": ["Art. 27", "14 dni", "odstąpienie"],
            "query_type": "factual",
        },
    ]

    queries_file = OUTPUT_DIR / "test_queries.jsonl"
    with open(queries_file, "w", encoding="utf-8") as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(f"  test_queries.jsonl: {len(queries)} entries")

    # --- evaluation_pairs.jsonl ---
    eval_pairs = [
        {
            "id": "e-001",
            "input": "Przeanalizuj § 7 umowy sprzedaz_02 pod kątem zgodności z przepisami "
            "dotyczącymi wypowiedzenia umowy.",
            "expected_output": "Klauzula § 7 ust. 2 umowy sprzedaz_02 przewiduje 90-dniowy "
            "okres wypowiedzenia, co narusza Art. 4j ust. 3a Prawa energetycznego. "
            "Zgodnie z tym przepisem, odbiorca w gospodarstwie domowym może wypowiedzieć "
            "umowę z zachowaniem miesięcznego okresu wypowiedzenia. "
            "Zalecenie: zmienić okres wypowiedzenia na 1 miesiąc.",
            "metrics": ["correctness", "faithfulness", "relevance"],
        },
        {
            "id": "e-002",
            "input": "Czy OWU sprzedaży v1 jest zgodne z prawem?",
            "expected_output": "OWU sprzedaży v1 jest zgodne z analizowanymi przepisami "
            "prawa energetycznego i ustawy o prawach konsumenta. Nie wykryto niezgodności.",
            "metrics": ["correctness"],
        },
    ]

    eval_file = OUTPUT_DIR / "evaluation_pairs.jsonl"
    with open(eval_file, "w", encoding="utf-8") as f:
        for e in eval_pairs:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"  evaluation_pairs.jsonl: {len(eval_pairs)} entries")

    print(f"\nDone: ground-truth files saved to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
