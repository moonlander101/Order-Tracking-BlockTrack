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
    products = OrderProductSerializer(many=True)
    details = OrderDetailsSerializer()

    class Meta:
        model = Order
        fields = ['order_id', 'user_id', 'status', 'blockchain_tx_id', 'ipfs_hash', 'created_at', 'products', 'details']
        read_only_fields = ['order_id', 'created_at']

    def create(self, validated_data):
        # Extract details data
        details_data = validated_data.pop('details')
        products_data = validated_data.pop('products', [])

        # Create the order
        order = Order.objects.create(**validated_data)

        # Create the OrderDetails object
        OrderDetails.objects.create(order=order, **details_data)

        # Create OrderProduct objects if provided
        for prod in products_data:
            OrderProduct.objects.create(order=order, **prod)

        return order

class MinimalOrderSerializer(serializers.ModelSerializer):
    products = MinimalOrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_id', 'products']
