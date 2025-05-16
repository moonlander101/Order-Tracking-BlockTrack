from django.db import models

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    # product = models.CharField(max_length=255)
    user_id = models.IntegerField()
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"

class OrderDetails(models.Model):
    order = models.OneToOneField(Order, related_name='details', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=64)
    warehouse_id = models.IntegerField()
    warehouse_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    zipcode = models.CharField(max_length=16)
    instructions = models.TextField(blank=True, default="")
    latitude = models.CharField(max_length=32)
    longitude = models.CharField(max_length=32)

    def __str__(self):
        return f"Order {self.order.order_id} - Details"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='products', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    count = models.IntegerField()
    unit_price = models.FloatField()



