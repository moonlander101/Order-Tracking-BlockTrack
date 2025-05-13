from orders.models import Order
from .blockchain_utils import invoke_update_order_status

def update_order_status(order_id, status,timestamp, func=lambda: None):
    order = Order.objects.get(order_id = order_id)

    if (not order):
        raise Exception(f"No order by order_id: {order_id}")
    
    order.status = status

    order.save()

    invoke_update_order_status(order_id, status, timestamp)

    func()
