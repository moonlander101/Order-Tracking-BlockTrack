from .utils.endpoints import fetch_products, fetch_warehouse_details
from .utils.blockchain_utils import invoke_create_order, invoke_read_order, invoke_update_order_status
from . import send_to_kafka
from .models import Order
from .serializers import CreateOrderSerializer, MinimalOrderSerializer, OrderSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.utils import timezone
import logging

class ReadOrderView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            # Define query parameter "test"
            openapi.Parameter(
                'order_id', openapi.IN_QUERY, description="Id of the order", type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request):
        try:
            order_id = request.GET.get("order_id")
            if (not order_id or len(order_id) == 0):
                return Response({
                    "error": "order_id query param required"
            }, status=400)    
            result = invoke_read_order(order_id)
            return Response(result)
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

    @swagger_auto_schema(
        request_body=CreateOrderSerializer,
        responses={
            201: OrderSerializer(),
            400: 'Bad Request',
            500: 'Internal Server Error'
        },
        operation_description="Create a new order"
    )
    # Method is defined just for swagger to work properly
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.validated_data['status'] = 'pending'
        
        # Fetch prices from warehouse and add to data
        product_details = fetch_products()
        for p in serializer.validated_data['products']:
            product_id = p["product_id"]
            pd = [p for p in product_details if p["id"] == product_id]
            p['unit_price'] = pd[0]["unit_price"]

        order = serializer.save()
        
        # Register on blockchain
        try:
            timestamp = order.created_at.isoformat()
            
            invoke_create_order(
                order_id=str(order.order_id),
                timestamp=timestamp,
                status=order.status,
                order_type="ORD",
                documentHashes=[]  # Empty CID since we don't have a file
            )
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            # Log the error but keep the order in database
            # Use proper logging instead of print for Docker compatibility
            logger = logging.getLogger(__name__)
            logger.error(f"Blockchain registration failed: {str(e)}")
            
            headers = self.get_success_headers(serializer.data)
            return Response({
                "warning": "Order created in database but blockchain registration failed",
                "details": str(e),
                "order": serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)


class OrderByWarehouse(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'minimal', openapi.IN_QUERY,
                description="Option to reduce parameters to only order_id and products",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Filter orders by status",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, warehouse_id):
        try:
            status_param = request.query_params.get('status', None)
            queryset = Order.objects.filter(details__warehouse_id=warehouse_id)
            if status_param:
                queryset = queryset.filter(status=status_param)

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

    # Removed partial update and full update from the endpoints
    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    def partial_update(self, request, *args, **kwargs):
        if 'status' in request.data:
            order_id = kwargs.get('order_id')
            order = Order.objects.get(order_id=order_id)
            status = request.data['status']
            invoke_update_order_status(order_id, status, timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"))


            if (status == "accepted"):
                #TODO: Where to fetch this location from
                warehouse_location = request.data.get('warehouse_location')
                if(not warehouse_location):
                    return Response(
                        {
                            "error" : "Warehouse location must be provided for status to switch to 'accepted'"
                        },
                        status = 400
                    )

                event = {
                    "order_id": order_id,
                    "origin": {"lat": warehouse_location.get("latitude"), "lng":   warehouse_location.get("longitude")},
                    "destination": {"lat": order.details.longitude, "lng": order.details.latitude},
                    "demand": 10
                }
                send_to_kafka('orders.created', event)
            
        return super().partial_update(request, *args, **kwargs)


class UserOrderListView(APIView):
    def get(self, request, user_id):
        orders = Order.objects.filter(user_id=user_id)
        product_details = fetch_products()
        id_to_name = {str(p["id"]): p["product_name"] for p in product_details}

        serialized_orders = []
        for order in orders:
            order_data = OrderSerializer(order).data
            for product in order_data.get("products", []):
                product["product_name"] = id_to_name.get(str(product.get("product_id")))
            serialized_orders.append(order_data)

        return Response(serialized_orders)


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

            # Validate status against model choices if provided
            new_data = {}
            
            if new_status:
                valid_statuses = [choice[0] for choice in Order._meta.get_field('status').choices]
                
                if new_status not in valid_statuses:
                    return Response({
                        "error": "Invalid status value",
                        "status": new_status,
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                new_data['status'] = new_status

            # Create the event and push to kafka
            if new_status == "accepted":
                warehouse_id = order.details.warehouse_id
                warehouse_location = fetch_warehouse_details(warehouse_id)[0]

                if(not warehouse_location):
                    return Response(
                        {
                            "error" : "Warehouse not found"
                        },
                        status = 400
                    )
                
                if warehouse_location:
                    # Filter out the "° E" part in "79.8612° E" given by warehouse
                    origin_longitude = warehouse_location.get('location_x')[:-3].strip()
                    origin_latitude = warehouse_location.get('location_y')[:-3].strip()


                event = {
                    "order_id": order_id,
                    "origin": {"lat": origin_latitude, "lng":   origin_longitude},
                    "destination": {"lat": order.details.latitude, "lng": order.details.longitude},
                    "demand": 10
                }
                print(f"Sending to kafka, {event}")
                send_to_kafka('orders.created', event)
            
            invoke_update_order_status(order_id, request.data.get("status"), timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

            serializer = OrderSerializer(order, data=new_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
