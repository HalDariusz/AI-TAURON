#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# AlICjA (AI-TAURON) — Install / Purge Script
#
# Usage:
#   ./scripts/install.sh install     — full fresh install (infra + HLF + app)
#   ./scripts/install.sh purge       — stop everything, remove all data/volumes
#   ./scripts/install.sh reinstall   — purge + install (clean slate)
#   ./scripts/install.sh start       — start all services (after install)
#   ./scripts/install.sh stop        — stop all services gracefully
#   ./scripts/install.sh status      — show status of all services
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
HLF_DIR="$PROJECT_DIR/hlf"
TEST_NETWORK="$HLF_DIR/fabric-samples/test-network"
CONDA_PYTHON="/home/hdn/miniconda3/envs/ai-tauron/bin/python"
CONDA_STREAMLIT="/home/hdn/miniconda3/envs/ai-tauron/bin/streamlit"
CHANNEL="compliancech"
CHAINCODE="compliance-registry"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${BLUE}[AlICjA]${NC} $1"; }
ok()   { echo -e "${GREEN}  ✅ $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠️  $1${NC}"; }
err()  { echo -e "${RED}  ❌ $1${NC}"; }

wait_for() {
    local name="$1" url="$2" max="${3:-30}"
    echo -n "  Waiting for $name"
    for i in $(seq 1 "$max"); do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}OK${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    echo -e " ${RED}TIMEOUT${NC}"
    return 1
}

# ============================================================================
# PURGE — stop everything, remove all data
# ============================================================================
do_purge() {
    log "🗑️  PURGE — stopping and removing everything..."

    # 1. Stop app processes
    log "Stopping application processes..."
    kill "$(lsof -t -i:8000)" 2>/dev/null && ok "API stopped" || true
    kill "$(lsof -t -i:8501)" 2>/dev/null && ok "Streamlit stopped" || true
    kill "$(lsof -t -i:3001)" 2>/dev/null && ok "HLF proxy stopped" || true

    # 2. HLF network down
    if [ -d "$TEST_NETWORK" ]; then
        log "Stopping Hyperledger Fabric network..."
        cd "$TEST_NETWORK"
        export PATH="$HLF_DIR/fabric-samples/bin:$PATH"
        ./network.sh down 2>/dev/null || true
        sudo rm -rf organizations/fabric-ca/org1 \
                    organizations/fabric-ca/org2 \
                    organizations/fabric-ca/ordererOrg \
                    organizations/ordererOrganizations \
                    organizations/peerOrganizations \
                    channel-artifacts system-genesis-block 2>/dev/null || true
        # Restore git-tracked scripts that sudo rm may have deleted
        cd "$HLF_DIR/fabric-samples"
        git checkout -- test-network/organizations 2>/dev/null || true
        ok "HLF network removed"
    fi

    # 3. Docker Compose down + volumes
    log "Stopping Docker Compose services..."
    cd "$PROJECT_DIR"
    docker compose down -v 2>/dev/null || true
    ok "Docker services removed"

    # 4. Prune Docker
    log "Pruning Docker volumes and networks..."
    docker volume prune -f 2>/dev/null || true
    docker network prune -f 2>/dev/null || true
    ok "Docker pruned"

    # 5. Clean gateway proxy wallet
    rm -rf "$HLF_DIR/gateway-proxy/wallet" 2>/dev/null || true

    # 6. Clean .env (optional — keep for reinstall)
    # rm -f "$PROJECT_DIR/.env"

    log "🗑️  PURGE complete — system is clean"
}

# ============================================================================
# INSTALL — full fresh installation
# ============================================================================
do_install() {
    log "🚀 INSTALL — setting up AlICjA (Ciocia ALA)..."
    cd "$PROJECT_DIR"

    # --- .env ---
    if [ ! -f .env ]; then
        log "Creating .env from template..."
        cp .env.example .env
        # Set Bielik as default LLM
        echo -e "\nHLF_ENABLED=true" >> .env
        echo "HLF_GATEWAY_URL=http://localhost:3001" >> .env
        echo "HLF_CHANNEL=$CHANNEL" >> .env
        echo "HLF_CHAINCODE=$CHAINCODE" >> .env
        echo "LLM_MODEL_NAME=SpeakLeash/bielik-11b-v3.0-instruct:Q4_K_M" >> .env
        ok ".env created"
    else
        ok ".env already exists"
    fi

    # --- Step 1: Docker infra ---
    log "[1/6] Starting Docker infrastructure (Qdrant, PostgreSQL, MLflow)..."
    docker compose up -d qdrant postgres 2>&1 | tail -3
    docker compose up -d --build mlflow 2>&1 | tail -3

    wait_for "PostgreSQL" "http://localhost:5432" 15 2>/dev/null || \
        until docker compose exec -T postgres pg_isready -U ai_tauron > /dev/null 2>&1; do sleep 2; done
    wait_for "Qdrant" "http://localhost:6333/healthz" 15
    wait_for "MLflow" "http://localhost:5000/health" 20
    ok "Docker infrastructure ready"

    # --- Step 2: Ollama check ---
    log "[2/6] Checking Ollama (native)..."
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        MODELS=$(curl -sf http://localhost:11434/api/tags | python3 -c "
import json,sys
models=json.load(sys.stdin)['models']
for m in models:
    print(f\"    {m['name']} ({m['details']['parameter_size']})\")" 2>/dev/null)
        ok "Ollama running with models:"
        echo "$MODELS"
    else
        warn "Ollama not running — start it manually: ollama serve"
    fi

    # --- Step 3: Python deps ---
    log "[3/6] Installing Python dependencies..."
    if [ -f "$CONDA_PYTHON" ]; then
        ok "Using conda env: ai-tauron"
    else
        log "Creating conda env ai-tauron..."
        /home/hdn/miniconda3/bin/conda create -n ai-tauron python=3.12 -y 2>&1 | tail -2
    fi
    source /home/hdn/miniconda3/bin/activate ai-tauron 2>/dev/null || true
    pip install -e ".[dev,ui]" 2>&1 | tail -3
    ok "Python dependencies installed"

    # --- Step 4: Hyperledger Fabric ---
    log "[4/6] Setting up Hyperledger Fabric network..."

    # Download fabric if needed
    if [ ! -d "$HLF_DIR/fabric-samples" ]; then
        log "Downloading Fabric binaries and samples..."
        cd "$HLF_DIR"
        curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh
        chmod +x install-fabric.sh
        ./install-fabric.sh --fabric-version 2.5.10 --ca-version 1.5.12 docker binary samples
    fi

    export PATH="$HLF_DIR/fabric-samples/bin:$PATH"
    export FABRIC_CFG_PATH="$HLF_DIR/fabric-samples/config"

    cd "$TEST_NETWORK"
    ./network.sh up createChannel -c "$CHANNEL" -ca 2>&1 | tail -5
    ok "Fabric network up, channel '$CHANNEL' created"

    # --- Step 5: Deploy chaincode ---
    log "[5/6] Deploying chaincode: $CHAINCODE..."

    # Prepare chaincode Go module
    CHAINCODE_DIR="$HLF_DIR/chaincode-go"
    mkdir -p "$CHAINCODE_DIR"
    cp "$PROJECT_DIR/scripts/chaincode/compliance_registry.go" "$CHAINCODE_DIR/main.go"

    if [ ! -f "$CHAINCODE_DIR/go.mod" ]; then
        cat > "$CHAINCODE_DIR/go.mod" << 'GOMOD'
module compliance-registry

go 1.21

require github.com/hyperledger/fabric-contract-api-go v1.2.2
GOMOD
        cd "$CHAINCODE_DIR" && go mod tidy && go mod vendor 2>&1 | tail -2
    fi

    cd "$TEST_NETWORK"
    ./network.sh deployCC -ccn "$CHAINCODE" -ccp "$CHAINCODE_DIR" -ccl go -c "$CHANNEL" 2>&1 | tail -5
    ok "Chaincode '$CHAINCODE' deployed"

    # --- Step 6: Gateway proxy ---
    log "[6/6] Starting Fabric gateway proxy..."
    cd "$HLF_DIR/gateway-proxy"
    npm install --silent 2>&1 | tail -1
    CHANNEL="$CHANNEL" nohup node server.js > /tmp/fabric-proxy.log 2>&1 &
    wait_for "HLF proxy" "http://localhost:3001/api/health" 10
    ok "Gateway proxy running on port 3001"

    # --- Done ---
    echo ""
    log "🎉 INSTALL complete!"
    echo ""
    do_status
    echo ""
    log "Next: run './scripts/install.sh start' to launch API + dashboard"
}

# ============================================================================
# START — start app services (API + Streamlit)
# ============================================================================
do_start() {
    log "▶️  Starting AlICjA services..."
    cd "$PROJECT_DIR"

    # Check infra
    if ! curl -sf http://localhost:6333/healthz > /dev/null 2>&1; then
        err "Qdrant not running — run './scripts/install.sh install' first"
        exit 1
    fi

    # Start API
    if lsof -t -i:8000 > /dev/null 2>&1; then
        warn "API already running on port 8000"
    else
        nohup "$CONDA_PYTHON" -m uvicorn src.python.main:app \
            --host 0.0.0.0 --port 8000 > /tmp/ai-tauron-api.log 2>&1 &
        wait_for "API" "http://localhost:8000/api/v1/health" 60
        ok "FastAPI running on port 8000"
    fi

    # Start Streamlit
    if lsof -t -i:8501 > /dev/null 2>&1; then
        warn "Streamlit already running on port 8501"
    else
        nohup "$CONDA_STREAMLIT" run src/python/dashboard.py \
            --server.port 8501 --server.address 0.0.0.0 \
            --server.headless true > /tmp/streamlit.log 2>&1 &
        wait_for "Streamlit" "http://localhost:8501/_stcore/health" 15
        ok "Streamlit running on port 8501"
    fi

    # Start HLF proxy if not running
    if ! lsof -t -i:3001 > /dev/null 2>&1; then
        cd "$HLF_DIR/gateway-proxy"
        CHANNEL="$CHANNEL" nohup node server.js > /tmp/fabric-proxy.log 2>&1 &
        wait_for "HLF proxy" "http://localhost:3001/api/health" 10
        ok "HLF proxy running on port 3001"
    fi

    echo ""
    log "🟢 AlICjA is live!"
    echo ""
    echo "  👩‍⚖️ Ciocia ALA:  http://$(hostname -I | awk '{print $1}'):8501"
    echo "  🔌 API:          http://$(hostname -I | awk '{print $1}'):8000"
    echo "  📊 MLflow:       http://$(hostname -I | awk '{print $1}'):5000"
}

# ============================================================================
# STOP — stop app services gracefully
# ============================================================================
do_stop() {
    log "⏹️  Stopping AlICjA services..."

    kill "$(lsof -t -i:8000)" 2>/dev/null && ok "API stopped" || warn "API not running"
    kill "$(lsof -t -i:8501)" 2>/dev/null && ok "Streamlit stopped" || warn "Streamlit not running"
    kill "$(lsof -t -i:3001)" 2>/dev/null && ok "HLF proxy stopped" || warn "HLF proxy not running"

    log "⏹️  App services stopped (Docker infra still running)"
}

# ============================================================================
# STATUS — show all services status
# ============================================================================
do_status() {
    log "📋 System status:"
    echo ""

    check_service() {
        local name="$1" url="$2"
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "  ${GREEN}🟢${NC} $name"
        else
            echo -e "  ${RED}🔴${NC} $name"
        fi
    }

    echo "  --- Infrastructure ---"
    check_service "Qdrant         :6333" "http://localhost:6333/healthz"
    check_service "PostgreSQL     :5432" "http://localhost:5432" 2>/dev/null || \
        (docker compose exec -T postgres pg_isready -U ai_tauron > /dev/null 2>&1 && \
            echo -e "  ${GREEN}🟢${NC} PostgreSQL     :5432" || \
            echo -e "  ${RED}🔴${NC} PostgreSQL     :5432")
    check_service "MLflow         :5000" "http://localhost:5000/health"
    check_service "Ollama         :11434" "http://localhost:11434/api/tags"

    echo "  --- Blockchain ---"
    check_service "HLF Proxy      :3001" "http://localhost:3001/api/health"
    if docker ps --format '{{.Names}}' | grep -q peer0.org1 2>/dev/null; then
        echo -e "  ${GREEN}🟢${NC} HLF Peers"
    else
        echo -e "  ${RED}🔴${NC} HLF Peers"
    fi

    echo "  --- Application ---"
    check_service "FastAPI        :8000" "http://localhost:8000/api/v1/health"
    check_service "Ciocia ALA     :8501" "http://localhost:8501/_stcore/health"

    echo ""
    echo "  --- Docker containers ---"
    docker ps --format "  {{.Names}}: {{.Status}}" 2>/dev/null | head -15
}

# ============================================================================
# MAIN
# ============================================================================
case "${1:-}" in
    install)
        do_install
        ;;
    purge)
        echo -e "${RED}⚠️  This will DESTROY all data, volumes, and blockchain state!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            do_purge
        else
            echo "Aborted."
        fi
        ;;
    reinstall)
        echo -e "${RED}⚠️  REINSTALL = purge ALL data + fresh install${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            do_purge
            do_install
            do_start
        else
            echo "Aborted."
        fi
        ;;
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    status)
        do_status
        ;;
    *)
        echo "AlICjA (Ciocia ALA) — Install Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  install     Full fresh install (infra + HLF + Python deps)"
        echo "  purge       Stop everything, remove ALL data and volumes"
        echo "  reinstall   Purge + install (clean slate)"
        echo "  start       Start app services (API + Streamlit + HLF proxy)"
        echo "  stop        Stop app services (keep infra running)"
        echo "  status      Show status of all services"
        ;;
esac
