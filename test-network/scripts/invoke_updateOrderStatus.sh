#!/bin/bash


set -e

# Parse input JSON
ORDER_JSON=$1
ORDER_ID=$(echo "$ORDER_JSON" | jq -r '.Args[0]')
STATUS=$(echo "$ORDER_JSON" | jq -r '.Args[1]')
TIMESTAMP=$(echo "$ORDER_JSON" | jq -r '.Args[2]')

echo "📦 Order ID   : $ORDER_ID"
echo "📄 New Status : $STATUS"
echo " Timestamp : $TIMESTAMP"

# Set paths
BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
BIN_PATH="$BASE_DIR/bin"
CONFIG_PATH="$BASE_DIR/config"
TEST_NETWORK="$BASE_DIR/test-network"
ORG_PATH="$TEST_NETWORK/organizations"

# Set env
export PATH="$BIN_PATH:$PATH"
export FABRIC_CFG_PATH="$CONFIG_PATH"
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_TLS_ROOTCERT_FILE="$ORG_PATH/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
export CORE_PEER_MSPCONFIGPATH="$ORG_PATH/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
export CORE_PEER_ADDRESS=peer0.org1.example.com:7051

# 🛠 Invoke chaincode and capture TXID
set +e
RESULT=$(peer chaincode invoke \
  -o orderer.example.com:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls \
  --cafile "$ORG_PATH/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" \
  -C mychannel \
  -n ordercc \
  --peerAddresses peer0.org1.example.com:7051 \
  --tlsRootCertFiles "$ORG_PATH/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" \
  --peerAddresses peer0.org2.example.com:9051 \
  --tlsRootCertFiles "$ORG_PATH/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" \
  -c "{\"function\":\"UpdateOrderStatus\",\"Args\":[\"$ORDER_ID\",\"$STATUS\", \"$TIMESTAMP\"]}"
)

STATUS=$?
set -e

# Print and forward result
echo "$RESULT"

if [ $STATUS -ne 0 ]; then
  echo "❌ Chaincode invoke failed"
  exit 1
else
  echo "✅ Chaincode invoke successful"
  exit 0
fi
