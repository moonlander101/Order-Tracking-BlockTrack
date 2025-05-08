from rest_framework import serializers
from .models import Order, OrderDetails, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product_id', 'count', 'unit_price']

class OrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['warehouse_id', 'nearest_city', 'latitude', 'longitude']

class OrderSerializer(serializers.ModelSerializer):
    details = OrderDetailsSerializer()
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_id', 'user_id', 'status',
                  'blockchain_tx_id', 'ipfs_hash', 'created_at',
                  'details', 'products']
        read_only_fields = ['order_id', 'created_at']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        products_data = validated_data.pop('products')

        order = Order.objects.create(**validated_data)

        OrderDetails.objects.create(order=order, **details_data)

        for prod in products_data:
            OrderProduct.objects.create(order_id=order, **prod)

        return order