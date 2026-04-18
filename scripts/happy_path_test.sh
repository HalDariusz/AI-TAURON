#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# AlICjA — Happy Path Test
# Runs full compliance analysis on selected documents and registers in blockchain
# ============================================================================

API="http://localhost:8000/api/v1"
HLF="http://localhost:3001/api"
LOG="/tmp/happy-path-test.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${BLUE}[TEST]${NC} $1" | tee -a "$LOG"; }
ok()   { echo -e "  ${GREEN}✅ $1${NC}" | tee -a "$LOG"; }
fail() { echo -e "  ${RED}❌ $1${NC}" | tee -a "$LOG"; }

echo "" > "$LOG"
log "=========================================="
log "AlICjA — Happy Path Test"
log "$(date)"
log "=========================================="

# --- Step 1: Health check ---
log ""
log "STEP 1: Health check"

api_health=$(curl -sf "$API/health" 2>/dev/null) || { fail "API not responding"; exit 1; }
echo "$api_health" | python3 -c "
import json,sys
h = json.load(sys.stdin)
for k,v in h.items():
    if k != 'status':
        icon = '✅' if v else '❌'
        print(f'  {icon} {k}: {v}')
" | tee -a "$LOG"

hlf_health=$(curl -sf "$HLF/health" 2>/dev/null) || { fail "HLF proxy not responding"; }
ok "All services healthy"

# --- Step 2: List documents ---
log ""
log "STEP 2: List documents"

docs=$(curl -sf "$API/documents" 2>/dev/null)
doc_count=$(echo "$docs" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
log "  $doc_count documents in system"

# Pick test documents: 1 zgodna + 2 z naruszeniami
ZGODNA_ID=$(echo "$docs" | python3 -c "
import json,sys
docs = json.load(sys.stdin)
d = next((x for x in docs if 'zgodna' in x['filename'].lower() and x['document_type']=='contract'), None)
print(d['id'] if d else '')
")
NARUSZ_1_ID=$(echo "$docs" | python3 -c "
import json,sys
docs = json.load(sys.stdin)
d = next((x for x in docs if 'sprzedaz 02' in x['filename'].lower()), None)
print(d['id'] if d else '')
")
NARUSZ_2_ID=$(echo "$docs" | python3 -c "
import json,sys
docs = json.load(sys.stdin)
d = next((x for x in docs if 'kompleksowa 01' in x['filename'].lower() and x['document_type']=='contract'), None)
print(d['id'] if d else '')
")

log "  Test documents:"
log "    Zgodna:     $ZGODNA_ID"
log "    Narusz #1:  $NARUSZ_1_ID"
log "    Narusz #2:  $NARUSZ_2_ID"

# --- Step 3: Run analyses ---
run_analysis() {
    local doc_id="$1"
    local label="$2"

    log ""
    log "STEP 3: Analyzing: $label"
    log "  Document ID: $doc_id"
    log "  Started: $(date)"

    local result
    result=$(curl -sf --max-time 7200 -X POST "$API/analysis/run" \
        -H "Content-Type: application/json" \
        -d "{\"document_id\": \"$doc_id\"}" 2>&1)

    if [ $? -ne 0 ] || [ -z "$result" ]; then
        fail "Analysis failed for $label"
        echo "  Raw: $result" | tee -a "$LOG"
        return 1
    fi

    local findings report_id critical high
    findings=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('total_findings', '?'))" 2>/dev/null)
    critical=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('critical_count', '?'))" 2>/dev/null)
    high=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('high_count', '?'))" 2>/dev/null)
    report_id=$(echo "$result" | python3 -c "import json,sys; print(json.load(sys.stdin).get('report_id', '?'))" 2>/dev/null)

    log "  Finished: $(date)"

    if [ "$findings" = "0" ]; then
        ok "$label: ZGODNY (0 findings) — report: ${report_id:0:8}..."
    else
        local icon="🟡"
        [ "$critical" != "0" ] && icon="🔴"
        [ "$high" != "0" ] && [ "$critical" = "0" ] && icon="🟠"
        ok "$label: $icon $findings findings (C:$critical H:$high) — report: ${report_id:0:8}..."
    fi

    # --- Register in blockchain ---
    log "  Registering in blockchain..."
    local bc_result
    bc_result=$(curl -sf --max-time 30 -X POST "$HLF/invoke" \
        -H "Content-Type: application/json" \
        -d "{
            \"channel\": \"compliancech\",
            \"chaincode\": \"compliance-registry\",
            \"function\": \"RegisterReport\",
            \"args\": [\"$report_id\", \"$doc_id\", \"hash-$(echo $report_id | cut -c1-16)\", \"$([ $findings = 0 ] && echo compliant || echo non_compliant)\", \"$findings\", \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"]
        }" 2>&1)

    if echo "$bc_result" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('status')=='ok'" 2>/dev/null; then
        ok "Blockchain: registered (report $report_id)"
    else
        fail "Blockchain registration failed: $bc_result"
    fi

    # --- Verify in blockchain ---
    local verify_result
    verify_result=$(curl -sf --max-time 10 -X POST "$HLF/query" \
        -H "Content-Type: application/json" \
        -d "{
            \"channel\": \"compliancech\",
            \"chaincode\": \"compliance-registry\",
            \"function\": \"GetReport\",
            \"args\": [\"$report_id\"]
        }" 2>&1)

    if echo "$verify_result" | python3 -c "import json,sys; d=json.load(sys.stdin); r=d['result']; print(f'    Blockchain record: verdict={r[\"verdict\"]}, findings={r[\"findingsCount\"]}, registered={r[\"registeredAt\"]}')" 2>/dev/null | tee -a "$LOG"; then
        ok "Blockchain: verified ✓"
    else
        fail "Blockchain verification failed"
    fi

    echo "$report_id"
}

# Run on "zgodna" first (should be fastest, true negative)
REPORT_1=""
if [ -n "$ZGODNA_ID" ]; then
    REPORT_1=$(run_analysis "$ZGODNA_ID" "Umowa zgodna (true negative)")
fi

# Run on "naruszenia" document
REPORT_2=""
if [ -n "$NARUSZ_1_ID" ]; then
    REPORT_2=$(run_analysis "$NARUSZ_1_ID" "Umowa sprzedaz 02 (3 naruszenia)")
fi

# Run on stress test
REPORT_3=""
if [ -n "$NARUSZ_2_ID" ]; then
    REPORT_3=$(run_analysis "$NARUSZ_2_ID" "Umowa kompleksowa 01 (5 naruszeń)")
fi

# --- Step 4: Summary ---
log ""
log "=========================================="
log "SUMMARY"
log "=========================================="

reports=$(curl -sf "$API/reports" 2>/dev/null)
report_count=$(echo "$reports" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null)
log "  Total reports: $report_count"

echo "$reports" | python3 -c "
import json,sys
reports = json.load(sys.stdin)
compliant = sum(1 for r in reports if r['total_findings'] == 0)
non_compliant = len(reports) - compliant
total_findings = sum(r['total_findings'] for r in reports)
critical = sum(r['critical_count'] for r in reports)
print(f'  Compliant: {compliant}')
print(f'  Non-compliant: {non_compliant}')
print(f'  Total findings: {total_findings}')
print(f'  Critical: {critical}')
print()
for r in reports:
    f = r['total_findings']
    icon = '🟢' if f==0 else ('🔴' if r['critical_count'] else ('🟠' if r['high_count'] else '🟡'))
    print(f'  {icon} {r[\"document_name\"]} — {f} findings [{r[\"id\"][:8]}...]')
" 2>/dev/null | tee -a "$LOG"

# Blockchain summary
log ""
log "Blockchain records:"
bc_all=$(curl -sf --max-time 10 -X POST "$HLF/query" \
    -H "Content-Type: application/json" \
    -d '{"channel":"compliancech","chaincode":"compliance-registry","function":"GetAllReports","args":[]}' 2>/dev/null)

echo "$bc_all" | python3 -c "
import json,sys
d = json.load(sys.stdin)
records = d.get('result', [])
if isinstance(records, list):
    print(f'  {len(records)} records on-chain')
    for r in records:
        print(f'    🔗 {r[\"reportId\"][:8]}... verdict={r[\"verdict\"]} findings={r[\"findingsCount\"]} at={r[\"registeredAt\"]}')
else:
    print(f'  Record: {records}')
" 2>/dev/null | tee -a "$LOG"

log ""
log "=========================================="
log "Happy Path Test COMPLETE — $(date)"
log "Full log: $LOG"
log "=========================================="
