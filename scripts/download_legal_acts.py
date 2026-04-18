#!/usr/bin/env python3
"""Download Polish legal acts from ISAP (isap.sejm.gov.pl) for AI-TAURON MVP."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

LEGAL_ACTS = [
    {
        "id": "prawo_energetyczne",
        "name": "Prawo energetyczne (tekst jednolity 2026)",
        "pdf_url": "https://isap.sejm.gov.pl/isap.nsf/download.xsp/WDU20260000043/O/D20260043.pdf",
        "api_url": "https://api.sejm.gov.pl/eli/acts/DU/2026/43",
        "subdir": "prawo_energetyczne",
        "filename": "DU_2026_43.pdf",
    },
    {
        "id": "prawa_konsumenta",
        "name": "Ustawa o prawach konsumenta (tekst jednolity 2024)",
        "pdf_url": "https://isap.sejm.gov.pl/isap.nsf/download.xsp/WDU20240001796/O/D20241796.pdf",
        "api_url": "https://api.sejm.gov.pl/eli/acts/DU/2024/1796",
        "subdir": "prawa_konsumenta",
        "filename": "DU_2024_1796.pdf",
    },
]

DATA_DIR = Path(__file__).parent.parent / "data" / "legal_acts"


def download_act(act: dict, client: httpx.Client) -> bool:
    target_dir = DATA_DIR / act["subdir"]
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / act["filename"]

    if target_file.exists():
        print(f"  [SKIP] {act['name']} — already downloaded")
        return True

    print(f"  [DOWNLOAD] {act['name']}...")
    try:
        resp = client.get(act["pdf_url"], follow_redirects=True, timeout=60.0)
        resp.raise_for_status()
        target_file.write_bytes(resp.content)
        print(f"    Saved: {target_file} ({len(resp.content) / 1024:.0f} KB)")
    except httpx.HTTPError as e:
        print(f"    [ERROR] Failed to download PDF: {e}")
        return False

    # Fetch metadata from API
    try:
        meta_resp = client.get(act["api_url"], timeout=30.0)
        if meta_resp.status_code == 200:
            meta_file = target_dir / "metadata.json"
            meta_file.write_text(
                json.dumps(meta_resp.json(), ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"    Metadata saved: {meta_file}")
    except httpx.HTTPError:
        print("    [WARN] Could not fetch API metadata (non-critical)")

    return True


def main():
    print("=== AI-TAURON: Downloading legal acts from ISAP ===\n")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    ok = 0
    with httpx.Client() as client:
        for act in LEGAL_ACTS:
            if download_act(act, client):
                ok += 1

    print(f"\nDone: {ok}/{len(LEGAL_ACTS)} acts downloaded to {DATA_DIR}")
    return 0 if ok == len(LEGAL_ACTS) else 1


if __name__ == "__main__":
    sys.exit(main())
