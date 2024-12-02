from django.db import models
from django.conf import settings
from inventory_management.models import Product
from datetime import timedelta
from django.utils import timezone


class PromotionCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Discount percentage"
    )
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}"

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expiration_date and timezone.now() > self.expiration_date:
            return False
        return True

    def save(self, *args, **kwargs):
        if not self.expiration_date:
            self.expiration_date = self.created_at + timedelta(hours=72)
        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    promotion_code = models.ForeignKey(
        PromotionCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # if not self.pk:
        super().save(*args, **kwargs)

        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(hours=24)
            super().save(update_fields=["expires_at"])

    def has_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            self.is_active = False
            self.save()
            return True
        return False

    def __str__(self):
        return f"Cart of {self.user.first_name} (Active: {self.is_active})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price_at_addition = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart {self.cart.id}"

    @property
    def total_price(self):
        return self.quantity * self.price_at_addition


# Wishlist Model
class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} in {self.user.username}'s wishlist"
