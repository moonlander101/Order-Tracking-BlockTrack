#!/bin/bash

# 🚨 Fail on any error
set -e

# 🧾 Function JSON string passed as the first argument
ORDER_JSON=$1

# 🧠 Decode JSON using jq
ORDER_ID=$(echo "$ORDER_JSON" | jq -r '.Args[0]')
STATUS=$(echo "$ORDER_JSON" | jq -r '.Args[1]')
TIMESTAMP=$(echo "$ORDER_JSON" | jq -r '.Args[2]')
CID=$(echo "$ORDER_JSON" | jq -r '.Args[3]')

# 🧪 Optional: echo parsed values
echo "📦 Order ID   : $ORDER_ID"
echo "📄 Status     : $STATUS"
echo "⏰ Timestamp  : $TIMESTAMP"
echo "🧬 IPFS CID   : $CID"

# 🧠 Set up environment (relative to this script location)
SCRIPTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FABRIC_BASE="$SCRIPTDIR/../.."
CONFIG_PATH="$FABRIC_BASE/config"

TEST_NETWORK="$FABRIC_BASE/test-network"

export PATH="$FABRIC_BASE/bin:$PATH"
export FABRIC_CFG_PATH="$CONFIG_PATH"
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_TLS_ROOTCERT_FILE="$TEST_NETWORK/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
export CORE_PEER_MSPCONFIGPATH="$TEST_NETWORK/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
export CORE_PEER_ADDRESS=localhost:7051

# 🚀 Invoke the chaincode
peer chaincode invoke \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls \
  --cafile "$TEST_NETWORK/organizations/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem" \
  -C mychannel \
  -n ordercc \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles "$CORE_PEER_TLS_ROOTCERT_FILE" \
  -c "{\"function\":\"CreateOrder\",\"Args\":[\"$ORDER_ID\",\"$STATUS\",\"$TIMESTAMP\",\"$CID\"]}"
