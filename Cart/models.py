from django.db import models
from django.core.exceptions import ValidationError
from Product.models import Product 
from Account.models import User  

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_products')
    quantity = models.PositiveIntegerField(default=1)
    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.PositiveIntegerField(default=0)

    def clean(self):
        """Validate that quantity does not exceed product stock."""
        if self.quantity > self.product.stock:
            raise ValidationError(
                f"You cannot add more than {self.product.stock} items of {self.product.name}."
            )

    def save(self, *args, **kwargs):
        # Validate quantity
        self.clean()

        # Calculate total
        self.total = self.product.price * self.quantity

        super().save(*args, **kwargs)

        # Update product stock
        self.product.stock = self.product.stock - self.quantity
        self.product.save()

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} purchased worth {self.total}"
