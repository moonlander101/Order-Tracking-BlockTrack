from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from .models import SupplierRequest

class SupplierRequestTests(APITestCase):
    def setUp(self):
        self.now = timezone.now()
        self.supplier_request = SupplierRequest.objects.create(
            supplier_id=1,
            created_at=self.now,
            expected_delivery_date=self.now,
            product_id=101,
            count=50.0,
            status='pending',
            received_at=None,
            warehouse_id=1,
            unit_price=20.5,
            quality=7,
            is_defective=False
        )
        self.base_url = '/api/v0/supplier-request/'

    def test_create_supplier_request(self):
        url = self.base_url
        data = {
            'supplier_id': 2,
            'created_at': timezone.now().isoformat(),
            'expected_delivery_date': timezone.now().isoformat(),
            'product_id': 102,
            'count': 75.0,
            'status': 'pending',
            'received_at': None,
            'warehouse_id': 1,
            'unit_price': 25.0,
            'quality': 9,
            'is_defective': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('request_id', response.data)

    def test_get_supplier_requests(self):
        url = self.base_url
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_get_supplier_request_by_id(self):
        url = f"{self.base_url}{self.supplier_request.request_id}/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['supplier_id'], self.supplier_request.supplier_id)

    def test_update_supplier_request_status(self):
        url = f"{self.base_url}{self.supplier_request.request_id}/status/"
        response = self.client.patch(url, {'status': 'received'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'received')

    def test_partial_update_supplier_request(self):
        url = f"{self.base_url}{self.supplier_request.request_id}/"
        patch_data = {
            'count': 60.0,
            'quality': 8,
            'is_defective': True
        }
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier_request.refresh_from_db()
        self.assertEqual(self.supplier_request.count, 60.0)
        self.assertEqual(self.supplier_request.quality, 8)
        self.assertTrue(self.supplier_request.is_defective)

    def test_delete_supplier_request(self):
        url = f"{self.base_url}{self.supplier_request.request_id}/"
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            SupplierRequest.objects.filter(request_id=self.supplier_request.request_id).exists()
        )

    def test_get_supplier_requests_by_warehouse(self):
        warehouse_id = self.supplier_request.warehouse_id
        url = f"{self.base_url}warehouse/{warehouse_id}/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for req in response.data:
            self.assertEqual(req['warehouse_id'], warehouse_id)
