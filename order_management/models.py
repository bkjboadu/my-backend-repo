from celery.app.utils import DEFAULTS
from django.db import models
from django.conf import settings
from inventory_management.models import Product
from django.utils import timezone
import uuid


# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
        ("failed_delivery", "Failed Delivery"),
        ("returned", "Returned"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    name = models.CharField(max_length=255,null=False,blank=False)
    email = models.EmailField(null=False,blank=False)
    phone_number = models.IntegerField(null=True,blank=True)
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="unpaid"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    return_requested = models.BooleanField(default=False)
    return_approved = models.BooleanField(default=False)
    return_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_number} by {self.user.first_name}"


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=20, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price_at_order
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.quantity} * {self.product.name} for Order {self.order.order_number}"
        )


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.order_number}"


# Shipment Model
class Shipment(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="shipment"
    )
    tracking_number = models.CharField(max_length=50, unique=True)
    carrier = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[
            ("in_transit", "In Transit"),
            ("delivered", "Delivered"),
            ("out_for_delivery", "Out for Delivery"),
            ("pending", "Pending"),
        ],
        default="pending",
    )
    estimated_delivery = models.DateTimeField()
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipment {self.tracking_number} for Order {self.order.order_number}"

    def mark_as_delivered(self):
        self.status = "delivered"
        self.delivered_at = timezone.now()
        self.save()

    def mark_as_shipped(self):
        self.status = "in_transit"
        self.shipped_at = timezone.now()
        self.save()
