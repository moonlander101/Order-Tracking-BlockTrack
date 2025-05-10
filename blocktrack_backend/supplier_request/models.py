from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class SupplierRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('received', 'Received'),
        ('returned', "Returned"),
        ('rejected', 'Rejected'),
    ]

    request_id = models.AutoField(primary_key=True)
    supplier_id = models.IntegerField()
    created_at = models.DateTimeField()
    expected_delivery_date = models.DateTimeField()
    product_id = models.IntegerField()
    count = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    received_at = models.DateTimeField(null=True, blank=True)
    warehouse_id = models.IntegerField()
    unit_price = models.FloatField(blank=True, null=True)
    quality = models.IntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(10)
    ], blank=True, null=True)
    is_defective = models.BooleanField(blank=True, null=True)
