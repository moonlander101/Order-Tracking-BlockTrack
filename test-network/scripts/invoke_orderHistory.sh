#!/bin/bash

set -e

ORDER_ID=$1

if [ -z "$ORDER_ID" ]; then
  echo '{"error": "Order ID is required"}'
  exit 1
fi

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

# Execute chaincode query
RESULT=$(peer chaincode query \
  --tls \
  --cafile "$ORG_PATH/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" \
  --peerAddresses peer0.org1.example.com:7051 \
  --tlsRootCertFiles "$ORG_PATH/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" \
  -C mychannel \
  -n ordercc \
  -c "{\"Args\":[\"GetOrderHistory\",\"$ORDER_ID\"]}"
)

STATUS=$?

if [ $STATUS -ne 0 ]; then
  echo "{\"error\": \"Failed to read order '$ORDER_ID' from blockchain\", \"details\": \"$RESULT\"}"
  exit 1
else
  echo "$RESULT"
  exit 0
fi