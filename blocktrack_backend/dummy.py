from supplier_request.models import SupplierRequest
from orders.models import Order, OrderDetails, OrderProduct
from django.utils import timezone
import random

statuses = ['pending', 'accepted', 'received', 'returned', 'rejected']

for _ in range(10):
    SupplierRequest.objects.create(
        supplier_id=random.randint(1, 5),
        created_at=timezone.now(),
        expected_delivery_date=timezone.now() + timezone.timedelta(days=random.randint(1, 10)),
        product_id=random.randint(100, 105),
        count=round(random.uniform(1, 100), 2),
        status=random.choice(statuses),
        received_at=timezone.now() if random.choice([True, False]) else None,
        warehouse_id=random.randint(1, 3),
        unit_price=round(random.uniform(10, 500), 2),
        quality=random.randint(0, 10) if random.choice([True, False]) else None,
        is_defective=random.choice([True, False, None])
    )

# Orders and OrderDetails dummy data
order_statuses = ['Pending', 'Accepted', 'Shipped', 'Delivered', 'Cancelled']
for i in range(5):
    order = Order.objects.create(
        user_id=i,
        status=random.choice(order_statuses),
        blockchain_tx_id=f"tx_{i:04}",
        ipfs_hash=f"QmHash{i:04}"
    )

    OrderDetails.objects.create(
        order=order,
        warehouse_id=random.randint(1000, 9999),
        nearest_city=f"City-{i}",
        latitude=f"{6.9 + i:.4f}",
        longitude=f"{79.8 + i:.4f}"
    )

    for j in range(3):
        OrderProduct.objects.create(
            order=order,
            product_id=100 + j,
            count=random.randint(1, 10),
            unit_price=round(random.uniform(10.0, 100.0), 2)
        )

print("Dummy data generation complete.")
