from django.db import models
from order_management.models import Order


class StripePayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id}"
    
class PaystackPayment(models.Model):    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='paystack_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)  
    status = models.CharField(max_length=20)  
    payment_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()  
    access_code = models.CharField(max_length=100, blank=True, null=True)  # Paystack access code for further actions

    def __str__(self):
        return f"Payment {self.reference} for Order {self.order.order_number}"

    class Meta:
        verbose_name = "Paystack Payment"
        verbose_name_plural = "Paystack Payments"