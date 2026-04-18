PROMPT_VERSION = "v1.1"

COMPLIANCE_ANALYSIS_TEMPLATE = """\
Jesteś ekspertem ds. zgodności regulacyjnej w sektorze energetycznym w Polsce.

Analizujesz poniższą klauzulę umowną pod kątem zgodności z obowiązującymi \
przepisami prawa energetycznego.

=== KLAUZULA UMOWNA ===
{contract_clause}

=== POWIĄZANE PRZEPISY PRAWNE ===
{legal_context}

Zadanie:
1. Oceń zgodność klauzuli z przytoczonymi przepisami.
2. Jeśli wykryjesz niezgodność, wskaż:
   - Na czym polega niezgodność
   - Który przepis jest naruszony (pełna referencja: artykuł, paragraf, ustęp)
   - Poziom ryzyka: critical / high / medium / low
   - Rekomendację zmiany klauzuli
3. Jeśli klauzula jest zgodna, potwierdź i uzasadnij.

Odpowiedz WYŁĄCZNIE w formacie JSON (bez dodatkowego tekstu):
{{
  "is_compliant": true/false,
  "findings": [
    {{
      "clause_text": "cytowany fragment klauzuli",
      "regulation_ref": "Art. X ust. Y ustawy ...",
      "description": "opis niezgodności",
      "severity": "critical|high|medium|low",
      "recommendation": "rekomendacja zmiany"
    }}
  ],
  "summary": "podsumowanie analizy"
}}
"""

DOCUMENT_ANALYSIS_TEMPLATE = """\
Jesteś ekspertem ds. zgodności regulacyjnej w sektorze energetycznym w Polsce.

Poniżej znajduje się spis treści / struktura dokumentu typu {document_type}.

=== STRUKTURA DOKUMENTU ===
{document_text}

=== WYMAGANIA PRAWNE ===
{legal_context}

Zadanie: Sprawdź czy dokument zawiera WSZYSTKIE wymagane elementy. \
Zgodnie z przepisami umowa sprzedaży energii elektrycznej dla konsumenta \
MUSI zawierać:

1. Informację o prawie odstąpienia od umowy w ciągu 14 dni \
   (Art. 27 ustawy o prawach konsumenta)
2. Informacje przedkontraktowe (Art. 5 ust. 4 PE + Art. 12 ustawy \
   o prawach konsumenta) — dane przedsiębiorcy, cechy świadczenia, \
   cena, prawo odstąpienia, czas trwania
3. Okres wypowiedzenia max 1 miesiąc (Art. 4j ust. 3a PE)
4. Procedurę reklamacyjną (Art. 5 ust. 2 pkt 4 PE)
5. Czas trwania umowy i warunki przedłużenia (Art. 5 ust. 2 pkt 2 PE)
6. Informację o strukturze paliw (Art. 5 ust. 6b PE)

Dla każdego BRAKUJĄCEGO elementu — zgłoś niezgodność. \
Dla każdej klauzuli, która NARUSZA przepisy — zgłoś niezgodność. \
Sprawdź też czy nie ma klauzul abuzywnych (Art. 385³ KC).

Odpowiedz WYŁĄCZNIE w formacie JSON (bez dodatkowego tekstu):
{{
  "findings": [
    {{
      "clause_text": "opis braku lub cytowany fragment",
      "regulation_ref": "Art. X ust. Y ustawy ...",
      "description": "opis niezgodności",
      "severity": "critical|high|medium|low",
      "recommendation": "rekomendacja"
    }}
  ],
  "summary": "podsumowanie analizy"
}}
"""
