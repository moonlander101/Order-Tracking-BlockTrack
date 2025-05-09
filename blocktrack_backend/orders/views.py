from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import generics, status
from .models import Order
from .serializers import MinimalOrderSerializer, OrderSerializer
import subprocess
import tempfile
import os
from .ipfs_utils import upload_to_ipfs
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
        print("📥 Received POST request")

        fabric_env = os.environ.copy()
        fabric_env["PATH"] = "/Users/ravishan/hyperledger-fabric/fabric-samples/bin:" + fabric_env["PATH"]
        fabric_env["FABRIC_CFG_PATH"] = "/Users/ravishan/hyperledger-fabric/fabric-samples/config"
        fabric_env["CORE_PEER_LOCALMSPID"] = "Org1MSP"
        fabric_env["CORE_PEER_TLS_ENABLED"] = "true"
        fabric_env["CORE_PEER_TLS_ROOTCERT_FILE"] = "/Users/ravishan/hyperledger-fabric/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt"
        fabric_env["CORE_PEER_MSPCONFIGPATH"] = "/Users/ravishan/hyperledger-fabric/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"
        fabric_env["CORE_PEER_ADDRESS"] = "localhost:7051"

        order_id = request.data.get("order_id")
        status = request.data.get("status")
        timestamp = request.data.get("timestamp")
        file = request.FILES.get("document")

        print("📝 order_id:", order_id)
        print("📝 status:", status)
        print("📝 timestamp:", timestamp)
        print("📎 file:", file.name if file else "No file")

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

            # Prepare command
            import json
            args_json = json.dumps({
                "function": "CreateOrder",
                "Args": [order_id, status, timestamp, cid]
            })
            script_path = "/Users/ravishan/hyperledger-fabric/fabric-samples/scripts/invoke_order.sh"

            command = f"{script_path} '{args_json}'"
            print("🚀 FULL PEER INVOKE COMMAND:\n", command)

            result = subprocess.run(command, shell=True, capture_output=True, text=True, env=fabric_env)

            print("✅ Blockchain STDOUT:\n", result.stdout)
            print("❌ Blockchain STDERR:\n", result.stderr)

            if result.returncode != 0:
                raise Exception("Chaincode invoke failed")

            return Response({"message": "Order created", "cid": cid, "blockchain_response": result.stdout})

        except Exception as e:
            return Response({
                "error": "Failed to create order",
                "details": str(e)
            }, status=500)


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
        print("FULL COMMAND:\n", command)


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


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

class OrderByWarehouse(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            # Define query parameter "test"
            openapi.Parameter(
                'minimal', openapi.IN_QUERY, description="Option to reduce parameters to only order_id and products", type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    def get(self, request, warehouse_id):
        queryset = Order.objects.filter(details__warehouse_id=warehouse_id)

        minimal = request.GET.get('minimal', False)

        if (eval(minimal[0].upper() + minimal[1:])):
            serializer = MinimalOrderSerializer(queryset, many=True)
        else:
            serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'


class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Order.objects.filter(user_id=user_id)


class OrderStatusUpdateView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['Pending', 'Accepted', 'Shipped', 'Delivered', 'Cancelled']
                )
            }
        ),
        responses={200: OrderSerializer()}
    )
    def patch(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
