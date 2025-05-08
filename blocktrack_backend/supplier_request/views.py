from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import SupplierRequest
from .serializers import SupplierRequestSerializer


class SupplierRequestListCreate(APIView):
    @swagger_auto_schema(
        request_body=SupplierRequestSerializer,
        responses={201: SupplierRequestSerializer()}
    )
    def post(self, request):
        serializer = SupplierRequestSerializer(data=request.data)
        if serializer.is_valid():
            # custom logic here
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(
    #     manual_parameters=[
    #         openapi.Parameter(
    #             'request_id', openapi.IN_QUERY,
    #             description="Optional request_id to filter",
    #             type=openapi.TYPE_STRING
    #         )
    #     ],
    #     responses={200: SupplierRequestSerializer(many=True)}
    # )
    def get(self, request):
        requests = SupplierRequest.objects.all()
        serializer = SupplierRequestSerializer(requests, many=True)
        return Response(serializer.data)


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
