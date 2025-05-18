from decimal import Decimal
from orders.utils.endpoints import fetch_products
from orders.utils.blockchain_utils import invoke_create_order, invoke_update_order_status
from .utils import add_price_competitiveness_score
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
import requests
from .models import SupplierRequest
from .serializers import SupplierRequestSerializer
# from datetime import datetime, timezone
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError

# Get service URLs from environment variables
user_service_url = os.environ.get('USER_SERVICE_URL', 'http://127.0.0.1:8002')
warehouse_service_url = os.environ.get('WAREHOUSE_SERVICE_URL', 'http://127.0.0.1:8001')

class SupplierRequestListCreate(APIView):
    def get_unit_price(self, product_id, supplier_id):
        response = requests.get(f"{warehouse_service_url}/api/product/supplier-products/")
        
        if response.status_code == 200:
            supplier_products = response.json()

            # Find the matching product for this supplier
            for item in supplier_products:
                if item['product'] == product_id and item['supplier_id'] == supplier_id:
                    return Decimal(item['supplier_price'])
            
            # If no match found, raise error
            raise Exception(f"No price found for product {product_id} from supplier {supplier_id}")
        else:
            raise Exception(f"Failed to get supplier products: {response.status_code}")

    @swagger_auto_schema(
        request_body=SupplierRequestSerializer,
        responses={201: SupplierRequestSerializer()}
    )
    def post(self, request):
        try:
            serializer = SupplierRequestSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                data['unit_price'] = self.get_unit_price(data["product_id"],data["supplier_id"])

                try:
                    instance = SupplierRequest(**data)
                    instance.full_clean()
                    instance.save()
                except ValidationError as e:
                    return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

                invoke_create_order(
                    order_id=instance.request_id,
                    timestamp=instance.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    status="Pending",
                    order_type="SR", 
                    documentHashes=[]
                )

                return Response(SupplierRequestSerializer(instance).data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "Failed to create supplier request",
                "details": str(e)
            }, status=500)
        
    
    def get(self, request):
        requests = SupplierRequest.objects.all()
        serializer = SupplierRequestSerializer(requests, many=True)
        return Response(serializer.data)



class SupplierRequestBySupplier(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Optional list of statuses to filter by. Can be a list of statuses like ?status=received&status=accepted.",
                type=openapi.TYPE_STRING,
                collectionFormat='multi',  # Allows multiple occurrences of the 'status' parameter
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="List of supplier requests with enriched product data",
                schema=SupplierRequestSerializer(many=True)
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def get(self, request, supplier_id):
        # Extract status from query parameter
        status = request.query_params.getlist('status')

        # Filter supplier requests by supplier_id and status
        reqs = SupplierRequest.objects.filter(supplier_id=supplier_id)
        if status:
            reqs = reqs.filter(status__in=status)

        serializer = SupplierRequestSerializer(reqs, many=True)
        data = serializer.data

        product_details = fetch_products()
        id_to_name = {str(p["id"]): p["product_name"] for p in product_details}

        # Enrich data with product information
        for item in data:
            try:
                product_id = item.get('product_id')
                product_name = id_to_name.get(str(product_id))
                if product_name:
                    item['product_name'] = product_name
                else:
                    item['product_name'] = 'Unknown'
            except Exception as e:
                item['product_name'] = 'Unknown'
                print(f"Error fetching product info: {str(e)}")

        return Response(data)

class SupplierRequestByWarehouse(APIView):
    def get(self, request, warehouse_id):
        requests = SupplierRequest.objects.filter(warehouse_id=warehouse_id)
        serializer = SupplierRequestSerializer(requests, many=True)
        return Response(serializer.data)


class SupplierRequestStatusUpdate(APIView):
    def patch(self, request, request_id):
        try:
            req = SupplierRequest.objects.get(request_id=request_id)
        except SupplierRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if 'status' not in request.data:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        # custom logic here
        req.status = request.data['status']
        
        invoke_update_order_status(request_id, request.data.get("status"), timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

        if req.status == "received" and not req.received_at:
            req.received_at = timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        req.save()
        return Response(SupplierRequestSerializer(req).data)


class SupplierRequestGetOrPartialUpdate(APIView):
    def get(self, request, request_id):
        try:
            req = SupplierRequest.objects.get(request_id=request_id)
        except SupplierRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierRequestSerializer(req)
        return Response(serializer.data)

    def patch(self, request, request_id):
        try:
            req = SupplierRequest.objects.get(request_id=request_id)
        except SupplierRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SupplierRequestSerializer(req, data=request.data, partial=True)
        if serializer.is_valid():
            new_status = request.data.get("status")

            if (new_status):
                invoke_update_order_status(request_id, request.data.get("status"), timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

            if new_status == "received" and not req.received_at:
                req.received_at = timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ")

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, request_id):
        try:
            req = SupplierRequest.objects.get(request_id=request_id)
        except SupplierRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        req.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SupplierRequestMetrics(APIView):
    def get(self, request, supplier_id):
        start_date = request.GET.get("start_date")
        queryset = SupplierRequest.objects.all()
        if start_date:
            start_date_parsed = parse_datetime(start_date)
            if start_date_parsed:
                queryset = queryset.filter(created_at__gt=start_date_parsed)
            else:
                return Response({"error": "Invalid start_date format"}, status=400)

        data = queryset.values(
            'is_defective', 'quality', 'count', 'unit_price', 'status',
            'expected_delivery_date', 'received_at', 'created_at', 'product_id', 'supplier_id'
        )

        data = add_price_competitiveness_score(data)
        data = [d for d in data if d['supplier_id'] == supplier_id]
        print(data)
        # Group data by product_id
        product_groups = {}
        for d in data:
            product_id = d.get('product_id')
            if product_id not in product_groups:
                product_groups[product_id] = []
            product_groups[product_id].append(d)

        # Calculate metrics per product
        product_metrics = []
        for product_id, product_data in product_groups.items():
            p_total = len(product_data)
            p_defective_count = sum(1 for d in product_data if d.get('is_defective'))
            p_returned_count = sum(1 for d in product_data if d.get('status') == "returned")
            p_received_count = sum(1 for d in product_data if d.get('status') == "received")
            p_q_sum = sum(d.get('quality', 0) or 0 for d in product_data)
            
            p_on_time_count = sum(
            1 for d in product_data if d.get('received_at') and d.get('expected_delivery_date') 
            and d['received_at'] <= d['expected_delivery_date']
            )
            
            p_responsiveness_values = []
            for d in product_data:
                received_at = d.get('received_at')
                created_at = d.get('created_at')
                expected_delivery_date = d.get('expected_delivery_date')
                if received_at and created_at and expected_delivery_date:
                    expected_duration = expected_delivery_date - created_at
                    actual_duration = received_at - created_at
                    if expected_duration.total_seconds() > 0:
                        ratio = actual_duration / expected_duration
                        normalized = min(max(ratio * 10, 0), 10)
                        p_responsiveness_values.append(normalized)
            
            p_accuracy_count = sum(
            1 for d in product_data if (
                d.get('status') == 'received' and 
                not d.get('is_defective') and 
                (d.get('quality') or 0) >= 8
            )
            )
            
            product_metrics.append({
                "product_id": product_id,
                "total_requests": p_total,
                "defective_count": p_defective_count,
                "defective_rate": p_defective_count / p_total if p_total > 0 else 0,
                "return_count": p_returned_count,
                "returned_rate": p_returned_count / p_total if p_total > 0 else 0,
                "quality_score": p_q_sum / p_total if p_total > 0 else 0,
                "on_time_delivery_rate": p_on_time_count / p_total if p_total > 0 else 0,
                "fill_rate": p_received_count / p_total if p_total > 0 else 0,
                "avg_responsiveness": sum(p_responsiveness_values) / len(p_responsiveness_values) if p_responsiveness_values else None,
                "order_accuracy_rate": p_accuracy_count / p_total if p_total > 0 else 0,
                "data" : product_groups[product_id]
            })

        return Response(product_metrics)
    

class SupplierRequestWithNames(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Optional status to filter supplier requests. Can be a single status or a list of statuses.",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="List of supplier requests with enriched data",
                schema=SupplierRequestSerializer(many=True)
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def get(self, request, warehouse_id):
        status_param = request.query_params.get('status', None)
    
        try:
            # Base query filtering by warehouse
            supplier_requests = SupplierRequest.objects.filter(warehouse_id=warehouse_id)
            
            # Apply status filtering if provided
            if status_param:
                # Split comma-separated statuses into a list
                status_list = [s.strip() for s in status_param.split(',')]
                supplier_requests = supplier_requests.filter(status__in=status_list)
                
        except Exception as e:
            print(f"Error filtering requests: {e}")
            # Fallback to all requests for this warehouse
            supplier_requests = SupplierRequest.objects.filter(warehouse_id=warehouse_id)

        serializer = SupplierRequestSerializer(supplier_requests, many=True)
        data = serializer.data

        # Enrich data with supplier names and product names
        product_details = fetch_products()
        id_to_name = {str(p["id"]): p["product_name"] for p in product_details}
        
        for item in data:
            # Fetch supplier name

            try:
                supplier_id = item.get('supplier_id')
                supplier_response = requests.get(f"{user_service_url}/api/v1/suppliers/{supplier_id}/info/")
                if supplier_response.status_code == 200:
                    supplier_data = supplier_response.json()
                    supplier_user_data = supplier_data.get('user')
                    print(supplier_data)
                    item['supplier_name'] = supplier_user_data.get('first_name', 'Unknown') + " " + supplier_user_data.get('last_name', 'Unknown')
                else:
                    item['supplier_name'] = 'Unknown'
            except Exception as e:
                item['supplier_name'] = 'Error fetching supplier'
                print(f"Error fetching supplier info: {str(e)}")
            
            # Fetch product name
            try:
                product_id = item.get('product_id')
                # product_response = requests.get(f"{warehouse_service_url}/api/product/products/{product_id}/")
                product_name = id_to_name.get(str(product_id))
                if product_name:
                    item['product_name'] = product_name
                else:
                    item['product_name'] = 'Unknown'
            except Exception as e:
                item['product_name'] = 'Error fetching product'
                print(f"Error fetching product info: {str(e)}")
                
        return Response(data)