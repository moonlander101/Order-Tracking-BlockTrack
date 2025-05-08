from rest_framework import serializers
from .models import Order, OrderDetails, OrderProduct

class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product_id', 'count', 'unit_price']

class MinimalOrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product_id', 'count']

class OrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['warehouse_id', 'nearest_city', 'latitude', 'longitude']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True, source='order_products')
    details = OrderDetailsSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'user_id', 'status', 'blockchain_tx_id', 'ipfs_hash', 'created_at', 'products', 'details']
        read_only_fields = ['order_id', 'created_at']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        products_data = validated_data.pop('products')

        order = Order.objects.create(**validated_data)
        OrderDetails.objects.create(order=order, **details_data)

        for prod in products_data:
            OrderProduct.objects.create(order_id=order, **prod)

        return order

class MinimalOrderSerializer(serializers.ModelSerializer):
    products = MinimalOrderProductSerializer(many=True, read_only=True, source='order_products')

    class Meta:
        model = Order
        fields = ['order_id', 'products']
