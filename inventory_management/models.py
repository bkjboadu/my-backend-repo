from django.core.files import storage
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from storages.backends.gcloud import GoogleCloudStorage


# Store Model: Represents each store or tenant
class Store(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Category Model
class Category(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("store", "name")

    def __str__(self):
        return self.name


# Supplier Model
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("store", "sku")

    def __str__(self):
        return self.name


# Product Variant Model (Optional)
class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=50, blank=True, null=True)
    memory_size = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ("product", "sku")

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# Product Image Model
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="media/product_images/", storage=GoogleCloudStorage()
    )
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"


# Variant Image Model
class VariantImage(models.Model):
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="media/variant_images/", storage=GoogleCloudStorage()
    )
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.variant.product.name} - {self.variant.name}"


# Product Review Model
class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"


# Stock Entry Model
class StockEntry(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="stock_entries"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_entries"
    )
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_updates",
    )

    def __str__(self):
        return f"{self.quantity} units for {self.product.name}"
