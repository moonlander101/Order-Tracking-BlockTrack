import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order, OrderDetails, OrderProduct

PRODUCTS = [
    {"id": 1, "unit_price": 1324.79},
    {"id": 2, "unit_price": 1990.68},
    {"id": 3, "unit_price": 894.08},
    {"id": 4, "unit_price": 1269.40},
    {"id": 5, "unit_price": 1951.60},
    {"id": 6, "unit_price": 900.01},
    {"id": 7, "unit_price": 267.38},
    {"id": 8, "unit_price": 1353.29},
    {"id": 9, "unit_price": 393.25},
    {"id": 10, "unit_price": 618.65},
]

WAREHOUSES = {
    "Colombo Central": 1,
    "Kurunegala Rock": 3
}

INSTRUCTIONS = [
    "", "Leave at gate", "Call before arrival", "Deliver between 9am-5pm", "Do not ring bell"
]

class Command(BaseCommand):
    help = 'Generate 10 dummy orders for each user_id 1 to 10'

    def handle(self, *args, **options):
        Order.objects.all().delete()
        OrderDetails.objects.all().delete()
        OrderProduct.objects.all().delete()

        for user_id in range(1, 11):
            for _ in range(10):
                order = Order.objects.create(
                    user_id=user_id,
                    status=random.choice(['pending', 'accepted', 'shipped', 'delivered']),
                    created_at=timezone.now()
                )

                warehouse_name = random.choice(list(WAREHOUSES.keys()))
                OrderDetails.objects.create(
                    order=order,
                    order_number=f"ORD{order.order_id:05}",
                    warehouse_id=WAREHOUSES[warehouse_name],
                    warehouse_name=warehouse_name,
                    first_name="John",
                    last_name="Doe",
                    phone="0771234567",
                    address="123 Test Street",
                    city="Test City",
                    state="Test State",
                    zipcode="12345",
                    instructions=random.choice(INSTRUCTIONS),
                    latitude="6.9271",
                    longitude="79.8612"
                )

                for _ in range(random.randint(1, 5)):
                    product = random.choice(PRODUCTS)
                    OrderProduct.objects.create(
                        order=order,
                        product_id=product["id"],
                        count=random.randint(1, 10),
                        unit_price=product["unit_price"]
                    )

        self.stdout.write(self.style.SUCCESS("Dummy vendor orders generated"))
