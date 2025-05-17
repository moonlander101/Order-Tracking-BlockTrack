from django.core.management.base import BaseCommand
from supplier_request.models import SupplierRequest
from django.utils import timezone
from datetime import timedelta
import random

WAREHOUSE_MAP = {
    "Colombo Central": 1,
    "Kandy Depot": 2,
    "Kurunegala Rock": 3
}

SUPPLIER_PRODUCTS = {
    101: [
        ("SKU010", "Kurunegala Rock"),
        ("SKU006", "Colombo Central"),
        ("SKU008", "Colombo Central"),
        ("SKU008", "Kurunegala Rock"),
        ("SKU001", "Kurunegala Rock")
    ],
    102: [
        ("SKU002", "Kurunegala Rock"),
        ("SKU004", "Kurunegala Rock"),
        ("SKU008", "Colombo Central"),
        ("SKU008", "Kurunegala Rock"),
        ("SKU003", "Colombo Central"),
        ("SKU003", "Kurunegala Rock")
    ],
    103: [
        ("SKU008", "Colombo Central"),
        ("SKU008", "Kurunegala Rock"),
        ("SKU001", "Kurunegala Rock")
    ]
}

def sku_to_product_id(sku):
    return int(sku.replace("SKU", ""))

class Command(BaseCommand):
    help = 'Insert dummy supplier requests'

    def handle(self, *args, **options):
        statuses = ['pending', 'accepted', 'received', 'returned', 'rejected']
        now = timezone.now()

        for supplier_id, products in SUPPLIER_PRODUCTS.items():
            for sku, warehouse_name in products:
                for _ in range(10):
                    created_at = now - timedelta(days=random.randint(1, 30))
                    expected_delivery_date = created_at + timedelta(days=5)
                    status = random.choice(statuses)
                    received_at = created_at + timedelta(days=6) if status == 'received' else None

                    count = random.randint(500, 2000) if status == 'received' else random.randint(10, 100)

                    SupplierRequest.objects.create(
                        supplier_id=supplier_id,
                        created_at=created_at,
                        expected_delivery_date=expected_delivery_date,
                        product_id=sku_to_product_id(sku),
                        count=count,
                        status=status,
                        received_at=received_at,
                        warehouse_id=WAREHOUSE_MAP[warehouse_name],
                        unit_price=round(random.uniform(100.0, 2000.0), 2),
                        quality=random.choice([None] + list(range(0, 11))),
                        is_defective=random.choice([None, True, False])
                    )

        self.stdout.write(self.style.SUCCESS('Dummy supplier requests inserted.'))
