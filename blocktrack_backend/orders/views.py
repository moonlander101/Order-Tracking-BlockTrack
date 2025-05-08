from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import generics
from .models import Order
from .serializers import OrderSerializer
import subprocess
import tempfile
import os
from .ipfs_utils import upload_to_ipfs
from django_filters.rest_framework import DjangoFilterBackend
from pathlib import Path

# 🔧 Dynamically determine project base
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # → blocktrack_backend/
FABRIC_BASE = PROJECT_ROOT / "test-network" / ".."
FABRIC_BASE = FABRIC_BASE.resolve()

BIN_PATH = FABRIC_BASE / "bin"
CONFIG_PATH = FABRIC_BASE / "config"
TEST_NETWORK = FABRIC_BASE / "test-network"
SCRIPT_PATH = FABRIC_BASE / "test-network" / "scripts" / "invoke_order.sh"
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
        print("📥 Received POST request")
        fabric_env = get_fabric_env()

        order_id = request.data.get("order_id")
        status = request.data.get("status")
        timestamp = request.data.get("timestamp")
        file = request.FILES.get("document")

        print(f"📝 order_id: {order_id}")
        print(f"📝 status: {status}")
        print(f"📝 timestamp: {timestamp}")
        print(f"📎 file: {file.name if file else 'No file'}")

        try:
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            print("📁 Temp file saved at:", tmp_path)

            # Upload to IPFS
            cid = upload_to_ipfs(tmp_path)
            print("🧬 IPFS CID:", cid)

            # Prepare chaincode invoke args
            import json
            args_json = json.dumps({
                "function": "CreateOrder",
                "Args": [order_id, status, timestamp, cid]
            })

            print("🔧 Executing:", SCRIPT_PATH, args_json)

            result = subprocess.run(
                [str(SCRIPT_PATH), args_json],
                capture_output=True,
                text=True,
                env=fabric_env
            )

            print("✅ STDOUT:", result.stdout)
            print("❌ STDERR:", result.stderr)

            if result.returncode != 0:
                raise Exception(f"Invoke script failed:\n{result.stderr}")

            return Response({
                "message": "Order created",
                "cid": cid,
                "blockchain_response": result.stdout.strip()
            })

        except Exception as e:
            return Response({
                "error": "Failed to create order",
                "details": str(e)
            }, status=500)


class ReadOrderView(APIView):
    def get(self, request, order_id):
        fabric_env = get_fabric_env()

        # Safely formatted single-line command
        command = [
            "peer", "chaincode", "query",
            "--tls",
            "--cafile", str(TEST_NETWORK / "organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"),
            "--peerAddresses", "localhost:7051",
            "--tlsRootCertFiles", str(TEST_NETWORK / "organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"),
            "-C", "mychannel",
            "-n", "ordercc",
            "-c", f'{{"Args":["ReadOrder", "{order_id}"]}}'
        ]

        print("🔍 Executing ReadOrder command for:", order_id)

        try:
            result = subprocess.run(command, capture_output=True, text=True, env=fabric_env)

            if result.returncode != 0:
                return Response({
                    "error": f"Failed to read order '{order_id}' from blockchain",
                    "details": result.stderr.strip()
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


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']


class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'
