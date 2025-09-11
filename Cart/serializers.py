from rest_framework import serializers
from .models import Cart, Product

class CartSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.last_name')  # explicitly declared field
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'product_name', 'quantity', 'total']
        # now 'user' is included

    def validate_quantity(self, value):
        product = self.instance.product if self.instance else Product.objects.get(id=self.initial_data.get('product'))
        if value > product.stock:
            raise serializers.ValidationError(f"You cannot add more than {product.stock} items of this product.")
        return value

    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity']
        if quantity > product.stock:
            raise serializers.ValidationError(f"You cannot add more than {product.stock} items of this product.")
        product.stock -= quantity
        product.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        product = instance.product
        old_quantity = instance.quantity
        new_quantity = validated_data.get('quantity', old_quantity)
        delta = new_quantity - old_quantity
        if delta > product.stock:
            raise serializers.ValidationError(f"You cannot add more than {product.stock} items of this product.")
        product.stock -= delta
        product.save()
        instance.quantity = new_quantity
        instance.total = product.price * new_quantity
        instance.save()
        return instance
