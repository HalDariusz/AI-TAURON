#!/usr/bin/env bash
set -euo pipefail

# AI-TAURON Hyperledger Fabric Bootstrap
# Generates crypto material, starts network, creates channel, deploys chaincode

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CHANNEL_NAME="compliance-channel"
CHAINCODE_NAME="compliance-registry"

echo "=== AI-TAURON: Hyperledger Fabric Bootstrap ==="

# --- Step 1: Download Fabric binaries if missing ---
if [ ! -f ./bin/cryptogen ]; then
    echo "[1/6] Downloading Fabric binaries..."
    curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.10 1.5.12 -d -s
    # This downloads fabric binaries to ./bin/ and docker images
else
    echo "[1/6] Fabric binaries already present"
fi

export PATH="$SCRIPT_DIR/bin:$PATH"

# --- Step 2: Generate crypto material ---
echo "[2/6] Generating crypto material..."
mkdir -p config/orderer config/peer config/fabric-ca

cat > crypto-config.yaml << 'CRYPTOEOF'
OrdererOrgs:
  - Name: Orderer
    Domain: tauron.example.com
    Specs:
      - Hostname: orderer

PeerOrgs:
  - Name: Tauron
    Domain: tauron.example.com
    EnableNodeOUs: true
    Template:
      Count: 1
    Users:
      Count: 1
CRYPTOEOF

cryptogen generate --config=crypto-config.yaml --output=crypto-config

# Copy MSP to config dirs
cp -r crypto-config/ordererOrganizations/tauron.example.com/orderers/orderer.tauron.example.com/msp config/orderer/
cp -r crypto-config/peerOrganizations/tauron.example.com/peers/peer0.tauron.example.com/msp config/peer/

# --- Step 3: Generate genesis block + channel tx ---
echo "[3/6] Generating genesis block and channel config..."

cat > configtx.yaml << 'CONFIGEOF'
Organizations:
  - &OrdererOrg
    Name: OrdererOrg
    ID: OrdererMSP
    MSPDir: crypto-config/ordererOrganizations/tauron.example.com/msp
    Policies:
      Readers:
        Type: Signature
        Rule: "OR('OrdererMSP.member')"
      Writers:
        Type: Signature
        Rule: "OR('OrdererMSP.member')"
      Admins:
        Type: Signature
        Rule: "OR('OrdererMSP.admin')"

  - &TauronOrg
    Name: TauronOrg
    ID: TauronMSP
    MSPDir: crypto-config/peerOrganizations/tauron.example.com/msp
    Policies:
      Readers:
        Type: Signature
        Rule: "OR('TauronMSP.admin', 'TauronMSP.peer', 'TauronMSP.client')"
      Writers:
        Type: Signature
        Rule: "OR('TauronMSP.admin', 'TauronMSP.client')"
      Admins:
        Type: Signature
        Rule: "OR('TauronMSP.admin')"
      Endorsement:
        Type: Signature
        Rule: "OR('TauronMSP.peer')"
    AnchorPeers:
      - Host: peer0.tauron.example.com
        Port: 7051

Capabilities:
  Channel: &ChannelCapabilities
    V2_0: true
  Orderer: &OrdererCapabilities
    V2_0: true
  Application: &ApplicationCapabilities
    V2_0: true

Application: &ApplicationDefaults
  Organizations:
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    LifecycleEndorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"
    Endorsement:
      Type: ImplicitMeta
      Rule: "MAJORITY Endorsement"
  Capabilities:
    <<: *ApplicationCapabilities

Orderer: &OrdererDefaults
  OrdererType: solo
  Addresses:
    - orderer.tauron.example.com:7050
  BatchTimeout: 2s
  BatchSize:
    MaxMessageCount: 10
    AbsoluteMaxBytes: 99 MB
    PreferredMaxBytes: 512 KB
  Organizations:
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
    BlockValidation:
      Type: ImplicitMeta
      Rule: "ANY Writers"

Channel: &ChannelDefaults
  Policies:
    Readers:
      Type: ImplicitMeta
      Rule: "ANY Readers"
    Writers:
      Type: ImplicitMeta
      Rule: "ANY Writers"
    Admins:
      Type: ImplicitMeta
      Rule: "MAJORITY Admins"
  Capabilities:
    <<: *ChannelCapabilities

Profiles:
  TauronGenesis:
    <<: *ChannelDefaults
    Orderer:
      <<: *OrdererDefaults
      Organizations:
        - *OrdererOrg
      Capabilities:
        <<: *OrdererCapabilities
    Consortiums:
      TauronConsortium:
        Organizations:
          - *TauronOrg

  TauronChannel:
    Consortium: TauronConsortium
    <<: *ChannelDefaults
    Application:
      <<: *ApplicationDefaults
      Organizations:
        - *TauronOrg
      Capabilities:
        <<: *ApplicationCapabilities
CONFIGEOF

mkdir -p channel-artifacts
configtxgen -profile TauronGenesis -channelID system-channel -outputBlock channel-artifacts/genesis.block
configtxgen -profile TauronChannel -outputCreateChannelTx channel-artifacts/${CHANNEL_NAME}.tx -channelID ${CHANNEL_NAME}

# Copy genesis block for orderer
cp channel-artifacts/genesis.block config/orderer/

# --- Step 4: Start network ---
echo "[4/6] Starting Fabric network..."
docker compose -f docker-compose.hlf.yml up -d
sleep 10

# --- Step 5: Create and join channel ---
echo "[5/6] Creating channel and joining peer..."

# Create channel
docker exec hlf-peer peer channel create \
  -o orderer.tauron.example.com:7050 \
  -c ${CHANNEL_NAME} \
  -f /etc/hyperledger/fabric/channel-artifacts/${CHANNEL_NAME}.tx \
  --outputBlock /etc/hyperledger/fabric/channel-artifacts/${CHANNEL_NAME}.block

# Join channel
docker exec hlf-peer peer channel join \
  -b /etc/hyperledger/fabric/channel-artifacts/${CHANNEL_NAME}.block

echo "[5/6] Peer joined channel: ${CHANNEL_NAME}"

# --- Step 6: Deploy chaincode ---
echo "[6/6] Deploying chaincode: ${CHAINCODE_NAME}..."

# Package chaincode
docker exec hlf-peer peer lifecycle chaincode package /tmp/${CHAINCODE_NAME}.tar.gz \
  --path /opt/gopath/src/${CHAINCODE_NAME} \
  --lang golang \
  --label ${CHAINCODE_NAME}_1.0

# Install
docker exec hlf-peer peer lifecycle chaincode install /tmp/${CHAINCODE_NAME}.tar.gz

# Get package ID
PACKAGE_ID=$(docker exec hlf-peer peer lifecycle chaincode queryinstalled | grep "${CHAINCODE_NAME}_1.0" | awk -F'[, ]+' '{print $3}')
echo "Package ID: ${PACKAGE_ID}"

# Approve
docker exec hlf-peer peer lifecycle chaincode approveformyorg \
  -o orderer.tauron.example.com:7050 \
  --channelID ${CHANNEL_NAME} \
  --name ${CHAINCODE_NAME} \
  --version 1.0 \
  --package-id ${PACKAGE_ID} \
  --sequence 1

# Commit
docker exec hlf-peer peer lifecycle chaincode commit \
  -o orderer.tauron.example.com:7050 \
  --channelID ${CHANNEL_NAME} \
  --name ${CHAINCODE_NAME} \
  --version 1.0 \
  --sequence 1

echo ""
echo "=== Fabric network ready ==="
echo "  Orderer:  localhost:7050"
echo "  Peer:     localhost:7051"
echo "  CA:       localhost:7054"
echo "  CouchDB:  localhost:5984"
echo "  Channel:  ${CHANNEL_NAME}"
echo "  Chaincode: ${CHAINCODE_NAME}"
