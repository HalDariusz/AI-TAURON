#!/usr/bin/env bash
set -euo pipefail

# AI-TAURON: Setup Hyperledger Fabric using official test-network
# This is the fastest path to a working HLF network for MVP

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CHANNEL_NAME="compliance-channel"
CHAINCODE_NAME="compliance-registry"
CHAINCODE_SRC="$SCRIPT_DIR/../scripts/chaincode"

echo "=== AI-TAURON: Hyperledger Fabric Setup ==="

# --- Step 1: Download Fabric samples + binaries ---
if [ ! -d "fabric-samples" ]; then
    echo "[1/5] Downloading Fabric samples, binaries, and Docker images..."
    curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh
    chmod +x install-fabric.sh
    ./install-fabric.sh --fabric-version 2.5.10 --ca-version 1.5.12 docker binary samples
else
    echo "[1/5] Fabric samples already present"
fi

export PATH="$SCRIPT_DIR/fabric-samples/bin:$PATH"
export FABRIC_CFG_PATH="$SCRIPT_DIR/fabric-samples/config"

# --- Step 2: Prepare chaincode ---
echo "[2/5] Preparing chaincode..."
CHAINCODE_DEST="$SCRIPT_DIR/fabric-samples/asset-transfer-basic/chaincode-go"
# Use our custom chaincode dir
mkdir -p "$SCRIPT_DIR/chaincode-go"
cp "$CHAINCODE_SRC/compliance_registry.go" "$SCRIPT_DIR/chaincode-go/main.go"

# Create go.mod for chaincode
cat > "$SCRIPT_DIR/chaincode-go/go.mod" << 'GOMOD'
module compliance-registry

go 1.21

require github.com/hyperledger/fabric-contract-api-go v1.2.2
GOMOD

# --- Step 3: Start test network ---
echo "[3/5] Starting Fabric test network..."
cd fabric-samples/test-network

./network.sh down 2>/dev/null || true
./network.sh up createChannel -c "$CHANNEL_NAME" -ca -s couchdb

echo "[3/5] Network up, channel '$CHANNEL_NAME' created"

# --- Step 4: Deploy chaincode ---
echo "[4/5] Deploying chaincode: $CHAINCODE_NAME..."
./network.sh deployCC \
    -ccn "$CHAINCODE_NAME" \
    -ccp "$SCRIPT_DIR/chaincode-go" \
    -ccl go \
    -c "$CHANNEL_NAME"

echo "[4/5] Chaincode deployed"

# --- Step 5: Test invoke ---
echo "[5/5] Testing chaincode..."
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

peer chaincode invoke \
    -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls \
    --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" \
    -C "$CHANNEL_NAME" \
    -n "$CHAINCODE_NAME" \
    --peerAddresses localhost:7051 \
    --tlsRootCertFiles "${CORE_PEER_TLS_ROOTCERT_FILE}" \
    --peerAddresses localhost:9051 \
    --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" \
    -c '{"function":"RegisterReport","Args":["test-001","doc-001","abc123hash","compliant","0","2026-04-18T12:00:00Z"]}'

sleep 2

peer chaincode query \
    -C "$CHANNEL_NAME" \
    -n "$CHAINCODE_NAME" \
    -c '{"Args":["GetReport","test-001"]}'

echo ""
echo "=== Fabric network ready ==="
echo "  Peer Org1:  localhost:7051 (TLS)"
echo "  Peer Org2:  localhost:9051 (TLS)"
echo "  Orderer:    localhost:7050 (TLS)"
echo "  CA Org1:    localhost:7054"
echo "  CA Org2:    localhost:8054"
echo "  CouchDB:    localhost:5984 / 7984"
echo "  Channel:    $CHANNEL_NAME"
echo "  Chaincode:  $CHAINCODE_NAME"
echo ""
echo "Next: start the REST gateway proxy"
