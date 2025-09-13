# models.py
from django.db import models
from Account.models import User
from Order.models import Order

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order_item = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    division = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    payment_id = models.CharField(max_length=100)  # store Stripe payment intent id
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_id} for order {self.order_item.order_id}"
