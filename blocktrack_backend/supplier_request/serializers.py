from rest_framework import serializers
from .models import SupplierRequest

class SupplierRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierRequest
        fields = '__all__'
        read_only_fields = ['unit_price']