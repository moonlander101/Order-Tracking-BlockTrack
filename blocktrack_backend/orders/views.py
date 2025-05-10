import json
from pathlib import Path
from . import send_to_kafka
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


# 🔧 Dynamically determine project base
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # → blocktrack_backend/
FABRIC_BASE = PROJECT_ROOT / "test-network" / ".."
FABRIC_BASE = FABRIC_BASE.resolve()

BIN_PATH = FABRIC_BASE / "bin"
CONFIG_PATH = FABRIC_BASE / "config"
TEST_NETWORK = FABRIC_BASE / "test-network"
SCRIPT_PATH = FABRIC_BASE / "test-network" / "scripts" / "invoke_the_chaincode.sh"
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

def invoke_create_order(order_id, timestamp, status, cid = ""):
    fabric_env = get_fabric_env()
    
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

    def create(self, request, *args, **kwargs):
        # Standard serializer validation
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set default status if not provided
        if 'status' not in serializer.validated_data:
            serializer.validated_data['status'] = 'Pending'
        
        # Save the order to database
        order = serializer.save()
        
        # Register on blockchain
        try:
            # Format timestamp
            timestamp = order.created_at.isoformat()
            
            # Call the blockchain function with order data
            invoke_create_order(
                order_id=str(order.order_id),
                timestamp=timestamp,
                status=order.status,
                cid=""  # Empty CID since we don't have a file
            )
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            # Log the error but keep the order in database
            print(f"Blockchain registration failed: {str(e)}")
            
            headers = self.get_success_headers(serializer.data)
            return Response({
                "warning": "Order created in database but blockchain registration failed",
                "details": str(e),
                "order": serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)

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
        try:
            queryset = Order.objects.filter(details__warehouse_id=warehouse_id)

            minimal = request.GET.get('minimal', False)

            if (eval(minimal[0].upper() + minimal[1:])):
                serializer = MinimalOrderSerializer(queryset, many=True)
            else:
                serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
                ),
                'warehouse_location': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description="Latitude of the warehouse"),
                        'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description="Longitude of the warehouse")
                    },
                    description="Location of the warehouse"
                )
            }
        ),
        responses={200: OrderSerializer()}
    )
    def patch(self, request, order_id):
        try:
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            new_status = request.data.get('status')
            warehouse_location = request.data.get('warehouse_location')
            
            new_data = {}

            if warehouse_location:
                origin_longitude = warehouse_location.get('longitude')
                origin_latitude = warehouse_location.get('latitude')
            
            # Validate status against model choices if provided
            if new_status:
                valid_statuses = [choice[0] for choice in Order._meta.get_field('status').choices]
                
                if new_status not in valid_statuses:
                    return Response({
                        "error": "Invalid status value",
                        "status": new_status,
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                new_data['status'] = new_status

            # Create the event and push to kafka
            event = {
                "order_id": order_id,
                "origin": {"lat": origin_latitude, "lng":   origin_longitude},
                "destination": {"lat": order.details.longitude, "lng": order.details.longitude},
                "demand": 10
            }
            send_to_kafka('orders.created', event)
            
            serializer = OrderSerializer(order, data=new_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
