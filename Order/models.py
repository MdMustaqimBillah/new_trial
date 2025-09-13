from django.db import models
from Account.models import User
from Cart.models import Cart
import uuid

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    carts = models.ManyToManyField(Cart, related_name='orders')
    purchased = models.BooleanField(default=False)
    total = models.PositiveIntegerField(default=0)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ordered at {self.created_at}"

    def calculate_total(self):
        self.total = sum(cart.total for cart in self.carts.all())
        super().calculate_total()
        
        return self.total

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
