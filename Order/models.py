from django.db import models
from Account.models import User
from Cart.models import Cart

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    carts = models.ManyToManyField(Cart, related_name='orders')
    ordered = models.BooleanField(default=False)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ordered at {self.created_at}"

    def calculate_total(self):
        self.total = sum(cart.total for cart in self.carts.all())
        super().calculate_total()
        
        return self.total
