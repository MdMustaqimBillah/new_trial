from rest_framework import serializers
from Account.models import User
from Cart.models import Cart
from Order.models import Order


class OrderSerializer(serializers.ModelSerializer):
    user=serializers.ReadOnlyField(source='user.email')
    cart=serializers.ReadOnlyField(source='cart.created_at')

    class Meta:
        model=Order
        fields=[
            'id',
        ]
        read_only_fields = [ 'total', 'ordered', 'created_at']