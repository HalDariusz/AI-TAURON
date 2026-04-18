#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# AlICjA — Seed & Test Script
#
# Fills the system with all MVP test data and optionally runs compliance
# analysis on each contract/OWU document.
#
# Usage:
#   ./scripts/seed_and_test.sh seed       — upload all documents (legal acts + contracts + OWU)
#   ./scripts/seed_and_test.sh analyze    — run compliance analysis on all contracts/OWU
#   ./scripts/seed_and_test.sh full       — seed + analyze (complete test run)
#   ./scripts/seed_and_test.sh status     — show what's in the system
#   ./scripts/seed_and_test.sh clean      — delete all documents and reports
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"
API="http://localhost:8000/api/v1"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${BLUE}[seed]${NC} $1"; }
ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "  ${RED}❌ $1${NC}"; }
info() { echo -e "  ${CYAN}ℹ️  $1${NC}"; }

# File to persist document IDs between seed and analyze steps
ID_FILE="/tmp/alicja-seed-ids.json"

# ============================================================================
# Check API is running
# ============================================================================
check_api() {
    if ! curl -sf "$API/health" > /dev/null 2>&1; then
        err "API not running at $API"
        echo "    Start it first: ./scripts/install.sh start"
        exit 1
    fi
}

# ============================================================================
# Upload a single document
# ============================================================================
upload_doc() {
    local file="$1"
    local doc_type="$2"
    local label="$3"

    local filename
    filename=$(basename "$file")

    echo -ne "  📤 ${label} (${filename})... "

    local response
    response=$(curl -sf --max-time 1800 -X POST "$API/documents/upload" \
        -F "file=@${file};filename=${filename}" \
        -F "document_type=${doc_type}" 2>&1) || {
        echo -e "${RED}FAIL${NC}"
        err "Upload failed: $response"
        return 1
    }

    local doc_id chunks
    doc_id=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['document_id'])" 2>/dev/null)
    chunks=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['chunk_count'])" 2>/dev/null)

    echo -e "${GREEN}OK${NC} — ${chunks} chunks (ID: ${doc_id:0:8}...)"

    # Save ID for later
    echo "$doc_id" >> /tmp/alicja-seed-ids-raw.txt
    echo "{\"id\": \"$doc_id\", \"file\": \"$filename\", \"type\": \"$doc_type\"}" >> /tmp/alicja-seed-docs.jsonl

    return 0
}

# ============================================================================
# SEED — upload all documents
# ============================================================================
do_seed() {
    check_api
    log "📦 SEED — uploading all MVP test data..."
    echo ""

    # Clean temp files
    rm -f /tmp/alicja-seed-ids-raw.txt /tmp/alicja-seed-docs.jsonl

    local uploaded=0
    local failed=0

    # --- Legal Acts ---
    log "📜 Legal Acts (baza wiedzy prawnej)"
    for pdf in "$DATA_DIR"/legal_acts/prawo_energetyczne/*.pdf \
               "$DATA_DIR"/legal_acts/prawa_konsumenta/*.pdf; do
        if [ -f "$pdf" ]; then
            if upload_doc "$pdf" "legal_act" "Akt prawny"; then
                ((uploaded++))
            else
                ((failed++))
            fi
        fi
    done

    echo ""

    # --- OWU ---
    log "📋 OWU (Ogólne Warunki Umów)"
    for owu in "$DATA_DIR"/owu/*.txt; do
        if [ -f "$owu" ]; then
            local name
            name=$(basename "$owu" .txt)
            if upload_doc "$owu" "owu" "OWU: $name"; then
                ((uploaded++))
            else
                ((failed++))
            fi
        fi
    done

    echo ""

    # --- Contracts ---
    log "📄 Umowy szczegółowe"
    for contract in "$DATA_DIR"/contracts/*.txt; do
        if [ -f "$contract" ]; then
            local name
            name=$(basename "$contract" .txt)
            if upload_doc "$contract" "contract" "Umowa: $name"; then
                ((uploaded++))
            else
                ((failed++))
            fi
        fi
    done

    echo ""
    log "📦 SEED complete: ${GREEN}${uploaded} uploaded${NC}, ${RED}${failed} failed${NC}"

    # Build ID file
    if [ -f /tmp/alicja-seed-docs.jsonl ]; then
        python3 -c "
import json
docs = []
with open('/tmp/alicja-seed-docs.jsonl') as f:
    for line in f:
        docs.append(json.loads(line))
with open('$ID_FILE', 'w') as f:
    json.dump(docs, f, indent=2)
print(f'  Saved {len(docs)} document IDs to $ID_FILE')
"
    fi
}

# ============================================================================
# ANALYZE — run compliance analysis on all contracts/OWU
# ============================================================================
do_analyze() {
    check_api
    log "🔍 ANALYZE — running compliance analysis on all contracts/OWU..."
    echo ""

    # Get all documents from API
    local docs
    docs=$(curl -sf "$API/documents" 2>/dev/null)
    if [ -z "$docs" ] || [ "$docs" = "[]" ]; then
        err "No documents in system. Run './scripts/seed_and_test.sh seed' first."
        exit 1
    fi

    # Filter to contracts and OWU only (skip legal_acts)
    local to_analyze
    to_analyze=$(echo "$docs" | python3 -c "
import json, sys
docs = json.load(sys.stdin)
targets = [d for d in docs if d['document_type'] in ('contract', 'owu')]
for d in targets:
    print(json.dumps(d))
" 2>/dev/null)

    if [ -z "$to_analyze" ]; then
        warn "No contracts/OWU to analyze."
        return
    fi

    local analyzed=0
    local total_findings=0
    local failed=0

    while IFS= read -r doc_json; do
        local doc_id doc_name doc_type
        doc_id=$(echo "$doc_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
        doc_name=$(echo "$doc_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['filename'])")
        doc_type=$(echo "$doc_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['document_type'])")

        local type_icon="📄"
        [ "$doc_type" = "owu" ] && type_icon="📋"

        echo -ne "  🔍 ${type_icon} ${doc_name}... "

        local result
        result=$(curl -sf --max-time 3600 -X POST "$API/analysis/run" \
            -H "Content-Type: application/json" \
            -d "{\"document_id\": \"$doc_id\"}" 2>&1) || {
            echo -e "${RED}FAIL${NC}"
            err "Analysis failed for $doc_name"
            ((failed++))
            continue
        }

        local findings critical high report_id
        findings=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)['total_findings'])" 2>/dev/null || echo "?")
        critical=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)['critical_count'])" 2>/dev/null || echo "?")
        high=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)['high_count'])" 2>/dev/null || echo "?")
        report_id=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin)['report_id'])" 2>/dev/null || echo "?")

        local status_icon="🟢"
        [ "$findings" != "0" ] && status_icon="🟡"
        [ "$critical" != "0" ] && status_icon="🔴"
        [ "$high" != "0" ] && [ "$critical" = "0" ] && status_icon="🟠"

        echo -e "${GREEN}OK${NC} — ${status_icon} ${findings} findings (C:${critical} H:${high}) [${report_id:0:8}...]"

        ((analyzed++))
        total_findings=$((total_findings + findings))
    done <<< "$to_analyze"

    echo ""
    log "🔍 ANALYZE complete: ${analyzed} analyzed, ${total_findings} total findings, ${failed} failed"
}

# ============================================================================
# STATUS — show what's in the system
# ============================================================================
do_status() {
    check_api
    log "📋 System data status"
    echo ""

    # Documents
    local docs
    docs=$(curl -sf "$API/documents" 2>/dev/null)
    local doc_count
    doc_count=$(echo "$docs" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

    log "📄 Documents: $doc_count"
    if [ "$doc_count" != "0" ]; then
        echo "$docs" | python3 -c "
import json, sys
docs = json.load(sys.stdin)
type_icons = {'legal_act': '📜', 'owu': '📋', 'contract': '📄'}
for d in docs:
    icon = type_icons.get(d['document_type'], '📄')
    date = d['uploaded_at'][:10]
    print(f\"  {icon} {d['filename']} ({d['document_type']}) — {date} [{d['id'][:8]}...]\")
" 2>/dev/null
    fi

    echo ""

    # Reports
    local reports
    reports=$(curl -sf "$API/reports" 2>/dev/null)
    local report_count
    report_count=$(echo "$reports" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

    log "📊 Reports: $report_count"
    if [ "$report_count" != "0" ]; then
        echo "$reports" | python3 -c "
import json, sys
reports = json.load(sys.stdin)
for r in reports:
    f = r['total_findings']
    c = r['critical_count']
    h = r['high_count']
    icon = '🟢' if f == 0 else ('🔴' if c > 0 else ('🟠' if h > 0 else '🟡'))
    date = r['created_at'][:10]
    print(f\"  {icon} {r['document_name']} — {f} findings (C:{c} H:{h}) — {date} [{r['id'][:8]}...]\")
" 2>/dev/null
    fi

    echo ""

    # Summary
    if [ "$report_count" != "0" ]; then
        echo "$reports" | python3 -c "
import json, sys
reports = json.load(sys.stdin)
total = len(reports)
compliant = sum(1 for r in reports if r['total_findings'] == 0)
non_compliant = total - compliant
all_findings = sum(r['total_findings'] for r in reports)
critical = sum(r['critical_count'] for r in reports)
high = sum(r['high_count'] for r in reports)
print(f'  --- Summary ---')
print(f'  Reports:        {total}')
print(f'  Compliant:      {compliant}')
print(f'  Non-compliant:  {non_compliant}')
print(f'  Total findings: {all_findings}')
print(f'  Critical:       {critical}')
print(f'  High:           {high}')
" 2>/dev/null
    fi
}

# ============================================================================
# CLEAN — delete all documents and reports
# ============================================================================
do_clean() {
    check_api
    echo -e "${RED}⚠️  This will delete ALL documents and reports from the system!${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        return
    fi

    log "🗑️ Deleting all documents..."

    local docs
    docs=$(curl -sf "$API/documents" 2>/dev/null)
    local ids
    ids=$(echo "$docs" | python3 -c "
import json, sys
for d in json.load(sys.stdin):
    print(d['id'])
" 2>/dev/null)

    local deleted=0
    while IFS= read -r doc_id; do
        [ -z "$doc_id" ] && continue
        curl -sf -X DELETE "$API/documents/$doc_id" > /dev/null 2>&1 && ((deleted++))
    done <<< "$ids"

    ok "Deleted $deleted documents (+ associated reports)"
    rm -f "$ID_FILE" /tmp/alicja-seed-ids-raw.txt /tmp/alicja-seed-docs.jsonl
}

# ============================================================================
# MAIN
# ============================================================================
case "${1:-}" in
    seed)
        do_seed
        ;;
    analyze)
        do_analyze
        ;;
    full)
        do_seed
        echo ""
        echo "================================================"
        echo ""
        do_analyze
        echo ""
        echo "================================================"
        echo ""
        do_status
        ;;
    status)
        do_status
        ;;
    clean)
        do_clean
        ;;
    *)
        echo "AlICjA (Ciocia ALA) — Seed & Test Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  seed       Upload all MVP test documents (2 legal acts + 3 OWU + 5 contracts)"
        echo "  analyze    Run compliance analysis on all contracts/OWU"
        echo "  full       Seed + analyze + show status (complete test run)"
        echo "  status     Show documents and reports in the system"
        echo "  clean      Delete all documents and reports"
        ;;
esac
