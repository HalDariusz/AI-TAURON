#!/usr/bin/env python3
"""AlICjA — Happy Path Test (Python, no curl timeouts)."""

import json
import sys
import time

import httpx

API = "http://localhost:8000/api/v1"
HLF = "http://localhost:3001/api"
client = httpx.Client(timeout=7200.0)  # 2h timeout


def log(msg):
    print(f"\033[0;34m[TEST]\033[0m {msg}", flush=True)


def ok(msg):
    print(f"  \033[0;32m✅ {msg}\033[0m", flush=True)


def fail(msg):
    print(f"  \033[0;31m❌ {msg}\033[0m", flush=True)


def run_analysis(doc_id, label):
    log(f"")
    log(f"ANALYZING: {label}")
    log(f"  Document ID: {doc_id}")
    log(f"  Started: {time.strftime('%H:%M:%S')}")
    t0 = time.time()

    try:
        resp = client.post(
            f"{API}/analysis/run",
            json={"document_id": doc_id},
        )
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        fail(f"Analysis failed: {e}")
        return None

    dt = time.time() - t0
    findings = result.get("total_findings", 0)
    critical = result.get("critical_count", 0)
    high = result.get("high_count", 0)
    report_id = result.get("report_id", "?")

    icon = "🟢" if findings == 0 else ("🔴" if critical else ("🟠" if high else "🟡"))
    log(f"  Finished: {time.strftime('%H:%M:%S')} ({dt:.0f}s)")
    ok(f"{label}: {icon} {findings} findings (C:{critical} H:{high})")
    ok(f"Report ID: {report_id}")

    # Register in blockchain
    log(f"  Registering in blockchain...")
    verdict = "compliant" if findings == 0 else "non_compliant"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        bc_resp = client.post(
            f"{HLF}/invoke",
            json={
                "channel": "compliancech",
                "chaincode": "compliance-registry",
                "function": "RegisterReport",
                "args": [
                    report_id,
                    doc_id,
                    f"sha256-{report_id[:16]}",
                    verdict,
                    str(findings),
                    timestamp,
                ],
            },
            timeout=30.0,
        )
        bc_data = bc_resp.json()
        if bc_data.get("status") == "ok":
            ok(f"Blockchain: registered ✓")
        else:
            fail(f"Blockchain: {bc_data}")
    except Exception as e:
        fail(f"Blockchain registration: {e}")

    # Verify on blockchain
    try:
        vr = client.post(
            f"{HLF}/query",
            json={
                "channel": "compliancech",
                "chaincode": "compliance-registry",
                "function": "GetReport",
                "args": [report_id],
            },
            timeout=10.0,
        )
        record = vr.json().get("result", {})
        ok(
            f"Blockchain verified: verdict={record.get('verdict')}, "
            f"findings={record.get('findingsCount')}, "
            f"at={record.get('registeredAt')}"
        )
    except Exception as e:
        fail(f"Blockchain verify: {e}")

    return result


def main():
    log("=" * 50)
    log("AlICjA — Happy Path Test")
    log(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 50)

    # Health check
    log("")
    log("STEP 1: Health check")
    health = client.get(f"{API}/health").json()
    for k, v in health.items():
        if k != "status":
            print(f"  {'✅' if v else '❌'} {k}: {v}", flush=True)

    # List documents
    log("")
    log("STEP 2: Documents")
    docs = client.get(f"{API}/documents").json()
    log(f"  {len(docs)} documents in system")

    # Find test documents
    contracts = [d for d in docs if d["document_type"] in ("contract", "owu")]

    # Pick 3 documents for test
    targets = []

    # 1. Zgodna (true negative)
    zgodna = next(
        (d for d in contracts if "zgodna" in d["filename"].lower()),
        None,
    )
    if zgodna:
        targets.append((zgodna["id"], f"✅ {zgodna['filename']} (true negative)"))

    # 2. Naruszenia
    narusz = next(
        (d for d in contracts if "sprzedaz 02" in d["filename"].lower()),
        None,
    )
    if narusz:
        targets.append((narusz["id"], f"⚠️ {narusz['filename']} (3 naruszenia)"))

    # 3. Stress test
    stress = next(
        (d for d in contracts if "kompleksowa 01" in d["filename"].lower()),
        None,
    )
    if stress:
        targets.append((stress["id"], f"🔴 {stress['filename']} (5 naruszeń)"))

    log(f"  Selected {len(targets)} documents for analysis")
    for doc_id, label in targets:
        log(f"    {label} [{doc_id[:8]}...]")

    # Run analyses
    log("")
    log("STEP 3: Running analyses")
    results = []
    for doc_id, label in targets:
        r = run_analysis(doc_id, label)
        if r:
            results.append(r)

    # Summary
    log("")
    log("=" * 50)
    log("SUMMARY")
    log("=" * 50)

    reports = client.get(f"{API}/reports").json()
    log(f"  Total reports in system: {len(reports)}")

    compliant = sum(1 for r in reports if r["total_findings"] == 0)
    non_comp = len(reports) - compliant
    total_f = sum(r["total_findings"] for r in reports)
    critical = sum(r["critical_count"] for r in reports)

    log(f"  Compliant: {compliant}")
    log(f"  Non-compliant: {non_comp}")
    log(f"  Total findings: {total_f}")
    log(f"  Critical: {critical}")
    log("")

    for r in reports:
        f = r["total_findings"]
        c = r["critical_count"]
        h = r["high_count"]
        icon = "🟢" if f == 0 else ("🔴" if c else ("🟠" if h else "🟡"))
        log(f"  {icon} {r['document_name']} — {f} findings [{r['id'][:8]}...]")

    # Blockchain summary
    log("")
    log("BLOCKCHAIN RECORDS:")
    try:
        bc = client.post(
            f"{HLF}/query",
            json={
                "channel": "compliancech",
                "chaincode": "compliance-registry",
                "function": "GetAllReports",
                "args": [],
            },
            timeout=10.0,
        )
        records = bc.json().get("result", [])
        if isinstance(records, list):
            log(f"  {len(records)} records on-chain")
            for rec in records:
                log(
                    f"  🔗 {rec['reportId'][:8]}... "
                    f"verdict={rec['verdict']} "
                    f"findings={rec['findingsCount']} "
                    f"at={rec['registeredAt']}"
                )
    except Exception as e:
        fail(f"Blockchain query: {e}")

    log("")
    log(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 50)


if __name__ == "__main__":
    main()
