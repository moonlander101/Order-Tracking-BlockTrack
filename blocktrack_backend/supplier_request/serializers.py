from rest_framework import serializers
from .models import SupplierRequest

class SupplierRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierRequest
        fields = '__all__'