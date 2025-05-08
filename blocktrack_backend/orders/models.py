from django.db import models

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    product = models.CharField(max_length=255)
    customer = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[
        ('Preparing', 'Preparing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ])
    blockchain_tx_id = models.CharField(max_length=255)  # Fabric transaction ID
    ipfs_hash = models.CharField(max_length=255)         # IPFS CID
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

class OrderDetails(models.Model):
    order_id = models.ForeignKey(Order, related_name='details', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    count = models.IntegerField()
    warehouse_id = models.IntegerField()
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Order {self.order.order_id} - Product {self.product_id}"
