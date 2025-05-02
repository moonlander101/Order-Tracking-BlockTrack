from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import subprocess
import tempfile
import os
from .ipfs_utils import upload_to_ipfs

FABRIC_BASE = "/Users/ravishan/hyperledger-fabric/fabric-samples"
BIN_PATH = f"{FABRIC_BASE}/bin"
TEST_NETWORK = f"{FABRIC_BASE}/test-network"

def get_fabric_env():
    env = os.environ.copy()
    env["PATH"] = f"{BIN_PATH}:" + env["PATH"]
    env["FABRIC_CFG_PATH"] = f"{FABRIC_BASE}/config"
    env["CORE_PEER_LOCALMSPID"] = "Org1MSP"
    env["CORE_PEER_TLS_ENABLED"] = "true"
    env["CORE_PEER_TLS_ROOTCERT_FILE"] = f"{TEST_NETWORK}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
    env["CORE_PEER_MSPCONFIGPATH"] = f"{TEST_NETWORK}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
    env["CORE_PEER_ADDRESS"] = "localhost:7051"
    return env

class CreateOrderView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        fabric_env = get_fabric_env()

        order_id = request.data.get("order_id")
        status = request.data.get("status")
        timestamp = request.data.get("timestamp")
        file = request.FILES.get("document")

        if not all([order_id, status, timestamp, file]):
            return Response({"error": "Missing fields"}, status=400)

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Upload to IPFS
            cid = upload_to_ipfs(tmp_path)

            # Chaincode command
            command = f"""
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com \
--tls \
--cafile {TEST_NETWORK}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
--peerAddresses localhost:7051 \
--tlsRootCertFiles {TEST_NETWORK}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
--peerAddresses localhost:9051 \
--tlsRootCertFiles {TEST_NETWORK}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
--waitForEvent \
-C mychannel -n ordercc \
-c '{{"function":"CreateOrder","Args":["{order_id}", "{status}", "{timestamp}", "{cid}"]}}'
"""

            result = subprocess.run(command, shell=True, capture_output=True, text=True, env=fabric_env)

            if result.returncode != 0:
                return Response({
                    "error": "Blockchain invoke failed",
                    "stderr": result.stderr
                }, status=500)

            return Response({
                "message": "Order created",
                "cid": cid,
                "blockchain_response": result.stdout.strip()
            })

        except Exception as e:
            return Response({"error": "Internal server error", "details": str(e)}, status=500)


class ReadOrderView(APIView):
    def get(self, request, order_id):
        fabric_env = get_fabric_env()

        command = f"""
peer chaincode query \
--tls \
--cafile {TEST_NETWORK}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
--peerAddresses localhost:7051 \
--tlsRootCertFiles {TEST_NETWORK}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
-C mychannel -n ordercc \
-c '{{"Args":["ReadOrder", "{order_id}"]}}'
"""

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, env=fabric_env)

            if result.returncode != 0:
                return Response({
                    "error": f"Failed to read order '{order_id}' from blockchain",
                    "details": result.stderr
                }, status=404)

            return Response({
                "order_id": order_id,
                "blockchain_data": result.stdout.strip()
            })

        except Exception as e:
            return Response({
                "error": "Unexpected error",
                "details": str(e)
            }, status=500)
