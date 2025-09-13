# serializers.py
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    order = serializers.ReadOnlyField(source='order_item.order_id')

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'order', 'address', 'city', 'division', 'country', 'zip_code', 'payment_id'
        ]
        read_only_fields = ['payment_id']
