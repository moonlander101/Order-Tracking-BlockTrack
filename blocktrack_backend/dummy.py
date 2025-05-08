from supplier_request.models import SupplierRequest
from orders.models import Order, OrderDetails, OrderProduct
from django.utils import timezone
import random
import uuid

# Dummy data for SupplierRequest
statuses = ['pending', 'received']

for i in range(10):
    SupplierRequest.objects.create(
        supplier_id=random.randint(1, 5),
        created_at=timezone.now(),
        expected_delivery_date=timezone.now() + timezone.timedelta(days=random.randint(1, 10)),
        product_id=random.randint(100, 105),
        count=round(random.uniform(1, 100), 2),
        status=random.choice(statuses),
        received_at=timezone.now() if random.choice([True, False]) else None,
        warehouse_id=random.randint(1, 3),
        unit_price=round(random.uniform(10, 500), 2)
    )

# Dummy data for Order and OrderDetails
order_statuses = ['Preparing', 'Shipped', 'Delivered', 'Cancelled']

# Sample addresses
cities = ['Colombo', 'Kandy', 'Galle', 'Jaffna']
countries = ['Sri Lanka', 'India', 'USA', 'UK']
zipcodes = ['00100', '00200', '01000', '10001']

# Generate Orders

statuses = ['Pending', 'Accepted', 'Shipped', 'Delivered', 'Cancelled']

for i in range(5):
    order = Order.objects.create(
        user_id=i,
        status=random.choice(statuses),
        blockchain_tx_id=f"tx_{i:04}",
        ipfs_hash=f"QmHash{i:04}"
    )

    OrderDetails.objects.create(
        order_id=order,
        warehouse_id=random.randint(1000, 9999),
        nearest_city=f"City-{i}",
        latitude=f"{6.9 + i:.4f}",
        longitude=f"{79.8 + i:.4f}"
    )

    for j in range(3):
        OrderProduct.objects.create(
            order_id=order,
            product_id=100 + j,
            count=random.randint(1, 10),
            unit_price=round(random.uniform(10.0, 100.0), 2)
        )

print("Dummy data generation complete.")
