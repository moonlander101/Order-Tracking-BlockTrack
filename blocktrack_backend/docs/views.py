from django.shortcuts import render
import json
from pathlib import Path

from orders.utils.blockchain_utils import invoke_read_order, invoke_add_docs
# from . import send_to_kafka
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from orders.models import Order
# from .serializers import MinimalOrderSerializer, OrderSerializer
import subprocess
import tempfile
import os
from orders.utils.ipfs_utils import get_ipfs_url, upload_to_ipfs
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.
class DocsCreate(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Upload documents for an order, remember to prefix with ORD_",
        manual_parameters=[
            openapi.Parameter(
                name="document",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Document file to upload"
            ),
            openapi.Parameter(
                name="order_id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="Order ID"
            )
        ],
        responses={
            200: openapi.Response("Document uploaded successfully"),
            400: openapi.Response("Bad request"),
            404: openapi.Response("Order not found"),
            500: openapi.Response("Internal server error")
        }
    )
    def post(self, request, order_id):
        file = request.FILES.get("document")

        if not order_id:
            return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not file:
            return Response({"error": "Document file is required"}, status=status.HTTP_400_BAD_REQUEST)

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
            print("🧬 IPFS URL:", get_ipfs_url(cid))

            # Update the order with the CID
            try:
                order = Order.objects.get(order_id=order_id)
                order.ipfs_hash = cid
                order.save()
            except Order.DoesNotExist:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


            invoke_add_docs(order_id, [cid])

            return Response({
                "message": "Document uploaded successfully",
                "cid": cid
            })

        except Exception as e:
            return Response({
                "error": "Failed to upload document",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class DocsList(APIView):
    @swagger_auto_schema(
        operation_description="Get document hashes for an order",
        manual_parameters=[
            openapi.Parameter(
                name="order_id", 
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="Order ID"
            )
        ],
        responses={
            200: openapi.Response("Document hashes retrieved successfully"),
            500: openapi.Response("Error retrieving document hashes")
        }
    )
    def get(self, request):
        order_id = request.query_params.get("order_id")
        try:
            data = invoke_read_order(order_id)
            blockchain_data = data.get('blockchain_data')
            return Response(
                {
                    "document_hashes" : blockchain_data.get('DocumentHashes')
                },
                status=200
            )
        except Exception as e:
            return Response(e, status=500)

class DocLinkGenerate(APIView):
    @swagger_auto_schema(
        operation_description="Generate IPFS links for documents of an order",
        manual_parameters=[
            openapi.Parameter(
                name="order_id", 
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="Order ID"
            )
        ],
        responses={
            200: openapi.Response("Document links generated successfully"),
            500: openapi.Response("Error generating document links")
        }
    )
    def get(self, request):
        order_id = request.query_params.get("order_id")
        try:
            data = invoke_read_order(order_id)
            blockchain_data = data.get('blockchain_data')
            res = {
                "docs" : dict()
            }
            for d in blockchain_data.get("DocumentHashes"):
                res['docs'][d] = get_ipfs_url(d)

            return Response(
                res, status=200
            )
        except Exception as e:
            return Response(e, status=500)
        