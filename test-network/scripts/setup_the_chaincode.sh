set -e

echo "🔁 Shutting down any previous network..."
./network.sh down

echo "🚀 Starting the network..."
./network.sh up createChannel -ca

echo "📦 Packaging chaincode..."
../bin/peer lifecycle chaincode package ordercc.tar.gz \
  --path ../chaincode-order \
  --lang golang \
  --label ordercc_1.0

echo "📥 Installing chaincode on Org1..."
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_ADDRESS=localhost:7051
export CORE_PEER_MSPCONFIGPATH=organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
../bin/peer lifecycle chaincode install ordercc.tar.gz

echo "📥 Installing chaincode on Org2..."
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_ADDRESS=localhost:9051
export CORE_PEER_MSPCONFIGPATH=organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
../bin/peer lifecycle chaincode install ordercc.tar.gz

PACKAGE_ID=$(../bin/peer lifecycle chaincode queryinstalled | grep "Package ID" | awk '{print $3}' | sed 's/,$//')
echo "🔑 Package ID: $PACKAGE_ID"

echo "✅ Approving chaincode for Org1..."
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_ADDRESS=localhost:7051
export CORE_PEER_MSPCONFIGPATH=organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
../bin/peer lifecycle chaincode approveformyorg \
  --channelID mychannel \
  --name ordercc \
  --version 1.0 \
  --package-id $PACKAGE_ID \
  --sequence 1 \
  --tls \
  --cafile organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  --orderer localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com

echo "✅ Approving chaincode for Org2..."
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_ADDRESS=localhost:9051
export CORE_PEER_MSPCONFIGPATH=organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
../bin/peer lifecycle chaincode approveformyorg \
  --channelID mychannel \
  --name ordercc \
  --version 1.0 \
  --package-id $PACKAGE_ID \
  --sequence 1 \
  --tls \
  --cafile organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  --orderer localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com

echo "📌 Committing chaincode definition..."
../bin/peer lifecycle chaincode commit \
  --channelID mychannel \
  --name ordercc \
  --version 1.0 \
  --sequence 1 \
  --tls \
  --orderer localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --cafile organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
  --peerAddresses localhost:9051 \
  --tlsRootCertFiles organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt

echo "✅ Chaincode deployed successfully! You're ready to use the backend."
