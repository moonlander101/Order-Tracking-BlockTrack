from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order
from orders.utils.blockchain_utils import invoke_create_order

class Command(BaseCommand):
    help = 'Invoke blockchain create_order for existing orders in DB'

    def handle(self, *args, **options):
        orders = Order.objects.all()
        for order in orders:
            invoke_create_order(
                order_id=order.order_id,
                status=order.status,
                order_type="ORD",
                timestamp=order.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                documentHashes=[]
            )
            self.stdout.write(f"Invoked create_order for order_id: {order.order_id}")
        self.stdout.write(self.style.SUCCESS("All orders invoked to blockchain"))