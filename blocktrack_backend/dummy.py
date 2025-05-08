from supplier_request.models import SupplierRequest
from orders.models import Order, OrderDetails
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
for i in range(15):
    order = Order.objects.create(
        product=f"Product {random.randint(1, 50)}",
        customer=f"Customer {random.randint(1, 20)}",
        status=random.choice(order_statuses),
        blockchain_tx_id=str(uuid.uuid4()),
        ipfs_hash=str(uuid.uuid4()),
        # created_at is auto_now_add
    )

    # Generate between 1 and 5 details for each order
    details_count = random.randint(1, 5)
    for _ in range(details_count):
        OrderDetails.objects.create(
            order_id=order,
            product_id=random.randint(100, 200),
            count=random.randint(1, 20),
            warehouse_id=random.randint(1, 5),
            address=f"{random.randint(1, 999)} Main Street",
            zipcode=random.choice(zipcodes),
            city=random.choice(cities),
            country=random.choice(countries)
        )

print("Dummy data generation complete.")
