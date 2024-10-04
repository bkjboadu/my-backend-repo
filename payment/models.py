from django.db import models
from order_management.models import Order

# Create your models here.
class StripePayment(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # e.g., 'succeeded', 'failed'
    created_at = models.DateTimeField(auto_now_add=True)
