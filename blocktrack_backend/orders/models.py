from django.db import models

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    # product = models.CharField(max_length=255)
    user_id = models.IntegerField()
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ])
    blockchain_tx_id = models.CharField(max_length=255, blank=True, null=True)
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

class OrderDetails(models.Model):
    order = models.OneToOneField(Order, related_name='details', on_delete=models.CASCADE)
    warehouse_id = models.IntegerField()
    nearest_city = models.CharField(max_length=255)
    latitude = models.CharField(max_length=32)
    longitude = models.CharField(max_length=32)

    def __str__(self):
        return f"Order {self.order.order_id} - Details"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='products', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    count = models.IntegerField()
    unit_price = models.FloatField()



