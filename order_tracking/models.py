from django.db import models
from order_management.models import Order


class OrderTracking(models.Model):
    STATUS_CHOICES = [
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("pending", "Pending"),
        ("out_for_delivery", "Out for Delivery"),
    ]
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="tracking_info"
    )
    tracking_number = models.CharField(max_length=100, unique=True)
    carrier = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    current_location = models.CharField(max_length=255, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking {self.tracking_number} for Order {self.order.order_number}"
