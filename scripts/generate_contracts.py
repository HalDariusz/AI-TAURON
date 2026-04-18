#!/usr/bin/env python3
"""Generate synthetic contracts and OWU for AI-TAURON MVP using Claude API.

Usage:
    pip install -r scripts/requirements-datagen.txt
    export ANTHROPIC_API_KEY=your_key
    python scripts/generate_contracts.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

try:
    import anthropic
except ImportError:
    print("ERROR: Install datagen deps first: pip install -r scripts/requirements-datagen.txt")
    sys.exit(1)

SPECS_FILE = Path(__file__).parent / "violation_specs.yaml"
DATA_DIR = Path(__file__).parent.parent / "data"

SYSTEM_PROMPT = """\
Jesteś ekspertem prawa energetycznego w Polsce. Generujesz realistyczne polskie \
dokumenty prawne: umowy sprzedaży energii elektrycznej i Ogólne Warunki Umów (OWU).

Zasady:
- Użyj realistycznych, ale fikcyjnych danych stron (nazwy firm, adresy, NIP)
- Język: formalny polski prawniczy
- Struktura umowy: §1 Przedmiot, §2 Definicje, §3 Warunki, §4 Cena, §5 Prawa, \
  §6 Odpowiedzialność, §7 Wypowiedzenie, §8 Odstąpienie, §9 Reklamacje, §10 RODO, \
  §11 Postanowienia końcowe
- Struktura OWU: Art. 1, Art. 2, ... z ustępami (ust. 1, ust. 2, ...)
- Dokument powinien mieć 3-5 stron tekstu
"""


def build_user_prompt(doc_spec: dict, violation_types: dict) -> str:
    doc_type = "OWU" if doc_spec["type"] == "owu" else "umowę"
    contract_type = doc_spec.get("contract_type", "sprzedaż")
    tariff = doc_spec.get("tariff_group", "G11")

    prompt = (
        f"Wygeneruj {doc_type} {'sprzedaży' if contract_type == 'sprzedaz' else contract_type} "
        f"energii elektrycznej dla odbiorcy w gospodarstwie domowym "
        f"(konsument, grupa taryfowa {tariff}).\n\n"
    )

    violations = doc_spec.get("violations", [])
    if violations:
        prompt += "Umowa MUSI zawierać następujące celowe niezgodności z prawem:\n"
        for i, v in enumerate(violations, 1):
            vtype = violation_types[v["type"]]
            prompt += (
                f"{i}. W {v['location']}: {v['detail']} "
                f"(naruszenie {vtype['regulation']})\n"
            )
        prompt += "\nReszta dokumentu musi być w pełni zgodna z prawem.\n"
    else:
        prompt += "Dokument musi być W PEŁNI ZGODNY z obowiązującym prawem.\n"

    prompt += f"\nID dokumentu: {doc_spec['id']}\n"
    return prompt


def generate_document(doc_spec: dict, violation_types: dict, client: anthropic.Anthropic) -> str:
    user_prompt = build_user_prompt(doc_spec, violation_types)

    print(f"  Generating {doc_spec['id']}...")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text


def save_as_text(text: str, doc_spec: dict) -> Path:
    """Save generated text. DOCX/PDF conversion requires manual step or additional tooling."""
    subdir = "owu" if doc_spec["type"] == "owu" else "contracts"
    output_dir = DATA_DIR / subdir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save as .txt first (conversion to DOCX/PDF is a separate step)
    output_file = output_dir / f"{doc_spec['id']}.txt"
    output_file.write_text(text, encoding="utf-8")
    return output_file


def main():
    print("=== AI-TAURON: Generating synthetic contracts ===\n")

    with open(SPECS_FILE, encoding="utf-8") as f:
        specs = yaml.safe_load(f)

    violation_types = specs["violation_types"]
    documents = [d for d in specs["documents"] if d.get("source") != "isap"]

    client = anthropic.Anthropic()

    generated = 0
    for doc_spec in documents:
        try:
            text = generate_document(doc_spec, violation_types, client)
            output_file = save_as_text(text, doc_spec)
            print(f"    Saved: {output_file}")
            generated += 1
        except Exception as e:
            print(f"    [ERROR] {doc_spec['id']}: {e}")

    print(f"\nDone: {generated}/{len(documents)} documents generated")
    print("NOTE: Generated as .txt — convert to DOCX/PDF manually or with convert script")
    return 0 if generated == len(documents) else 1


if __name__ == "__main__":
    sys.exit(main())
