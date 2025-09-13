from rest_framework import serializers
from Order.models import Order

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    carts = serializers.StringRelatedField(many=True)  # Show cart info

    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'user',
            'carts',
            'total',
            'purchased',
            'created_at'
        ]
        read_only_fields = ['total', 'purchased', 'created_at', 'order_id']
